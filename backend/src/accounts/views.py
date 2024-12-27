from django.utils import timezone
from django.contrib.auth import get_user_model, authenticate
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
import pyotp
import secrets
from .models import MFABackupCode
from .serializers import (
    UserRegistrationSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer,
    MFATokenSerializer,
    MFABackupCodeSerializer,
    LoginSerializer,
)
from django.core.exceptions import ValidationError

User = get_user_model()


class UserRegistrationView(generics.CreateAPIView):
    """View for user registration."""
    serializer_class = UserRegistrationSerializer
    
    def create(self, request, *args, **kwargs):
        """Handle user registration."""
        serializer = self.get_serializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'detail': 'Validation failed.',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Create the user
            user = serializer.save()
            
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'detail': 'Registration successful.',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'full_name': user.full_name,
                },
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            print(f"Registration error: {str(e)}")  # Log the actual error
            if hasattr(e, 'messages'):
                return Response({
                    'detail': 'Registration failed.',
                    'errors': e.messages
                }, status=status.HTTP_400_BAD_REQUEST)
            
            return Response({
                'detail': str(e),
                'errors': {
                    'non_field_errors': [str(e)]
                }
            }, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """View for user login."""
    
    def post(self, request):
        """Handle user login."""
        serializer = LoginSerializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            mfa_code = serializer.validated_data.get('mfa_code')
            
            user = authenticate(request, email=email, password=password)
            
            if not user:
                return Response({
                    'detail': 'Invalid credentials.',
                    'code': 'invalid_credentials'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            if user.mfa_enabled:
                if not mfa_code:
                    return Response({
                        'detail': 'MFA code required.',
                        'code': 'mfa_required',
                        'user_id': user.id
                    }, status=status.HTTP_401_UNAUTHORIZED)
                
                # Verify MFA code here
                # ...
            
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'detail': 'Login successful.',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'full_name': user.full_name,
                    'mfa_enabled': user.mfa_enabled,
                },
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            })
            
        except ValidationError as e:
            return Response({
                'detail': 'Validation failed.',
                'errors': e.messages
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                'detail': 'Login failed.',
                'errors': {
                    'non_field_errors': ['An unexpected error occurred. Please try again.']
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """View for user profile management."""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """Get the user profile."""
        return self.request.user


class ChangePasswordView(APIView):
    """View for password change."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """Handle password change."""
        serializer = ChangePasswordSerializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
            user = request.user
            
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({
                    'detail': 'Current password is incorrect.',
                    'errors': {
                        'old_password': ['Current password is incorrect.']
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
            
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            return Response({
                'detail': 'Password changed successfully.'
            })
            
        except ValidationError as e:
            return Response({
                'detail': 'Validation failed.',
                'errors': e.messages
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                'detail': 'Password change failed.',
                'errors': {
                    'non_field_errors': ['An unexpected error occurred. Please try again.']
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EnableMFAView(APIView):
    """View for enabling MFA."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if request.user.mfa_enabled:
            return Response(
                {'detail': 'MFA is already enabled.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Generate TOTP secret
        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret)
        
        # Create provisioning URI for QR code
        provisioning_uri = totp.provisioning_uri(
            request.user.email,
            issuer_name="Secure File Share"
        )

        # Save secret temporarily
        request.user.mfa_secret = secret
        request.user.save()

        return Response({
            'secret': secret,
            'provisioning_uri': provisioning_uri
        })


class DisableMFAView(APIView):
    """View for disabling MFA."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if not request.user.mfa_enabled:
            return Response(
                {'detail': 'MFA is not enabled.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Disable MFA and delete backup codes
        request.user.mfa_enabled = False
        request.user.mfa_secret = None
        request.user.save()
        request.user.backup_codes.all().delete()

        return Response({'detail': 'MFA disabled successfully.'})


class VerifyMFAView(APIView):
    """View for verifying MFA token."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = MFATokenSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=serializer.validated_data['user_id'])
        except User.DoesNotExist:
            return Response(
                {'detail': 'User not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if not user.mfa_enabled or not user.mfa_secret:
            return Response(
                {'detail': 'MFA is not enabled for this user.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verify TOTP token
        totp = pyotp.TOTP(user.mfa_secret)
        if not totp.verify(serializer.validated_data['token']):
            return Response(
                {'detail': 'Invalid token.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Generate tokens
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })


class GenerateBackupCodesView(APIView):
    """View for generating new backup codes."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if not request.user.mfa_enabled:
            return Response(
                {'detail': 'MFA must be enabled to generate backup codes.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Delete existing unused backup codes
        request.user.backup_codes.filter(used=False).delete()

        # Generate new backup codes
        backup_codes = []
        for _ in range(10):  # Generate 10 backup codes
            code = secrets.token_hex(4)  # 8 characters long
            backup_codes.append(
                MFABackupCode.objects.create(
                    user=request.user,
                    code=code
                )
            )

        serializer = MFABackupCodeSerializer(backup_codes, many=True)
        return Response(serializer.data)


class VerifyBackupCodeView(APIView):
    """View for verifying backup codes during login."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        code = request.data.get('code')
        user_id = request.data.get('user_id')

        if not code or not user_id:
            return Response(
                {'detail': 'Code and user_id are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            backup_code = MFABackupCode.objects.get(
                user_id=user_id,
                code=code,
                used=False
            )
        except MFABackupCode.DoesNotExist:
            return Response(
                {'detail': 'Invalid backup code.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Mark the code as used
        backup_code.used = True
        backup_code.used_at = timezone.now()
        backup_code.save()

        # Generate tokens
        refresh = RefreshToken.for_user(backup_code.user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })
