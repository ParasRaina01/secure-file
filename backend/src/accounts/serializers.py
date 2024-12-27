from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers
from .models import MFABackupCode

User = get_user_model()


class MFABackupCodeSerializer(serializers.ModelSerializer):
    """Serializer for MFA backup codes."""
    class Meta:
        model = MFABackupCode
        fields = ['code', 'used', 'created_at', 'used_at']
        read_only_fields = ['used', 'created_at', 'used_at']


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile data."""
    backup_codes = MFABackupCodeSerializer(many=True, read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'mfa_enabled', 'backup_codes']
        read_only_fields = ['id', 'email', 'backup_codes']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    email = serializers.EmailField(
        required=True,
        error_messages={
            'required': 'Email is required.',
            'invalid': 'Please enter a valid email address.',
            'blank': 'Email cannot be blank.'
        }
    )
    full_name = serializers.CharField(
        required=True,
        min_length=2,
        max_length=255,
        error_messages={
            'required': 'Full name is required.',
            'min_length': 'Full name must be at least 2 characters long.',
            'max_length': 'Full name cannot be longer than 255 characters.',
            'blank': 'Full name cannot be blank.'
        }
    )
    password = serializers.CharField(
        required=True,
        write_only=True,
        error_messages={
            'required': 'Password is required.',
            'blank': 'Password cannot be blank.'
        }
    )
    confirmPassword = serializers.CharField(
        required=True,
        write_only=True,
        error_messages={
            'required': 'Password confirmation is required.',
            'blank': 'Password confirmation cannot be blank.'
        }
    )
    
    class Meta:
        model = User
        fields = ['email', 'full_name', 'password', 'confirmPassword']
    
    def validate_email(self, value):
        """Validate email uniqueness and format."""
        value = value.lower().strip()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
    
    def validate_password(self, value):
        """Validate password using Django's password validation."""
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value
    
    def validate(self, data):
        """Validate the entire payload."""
        if not data.get('email'):
            raise serializers.ValidationError({
                'email': 'Email is required.'
            })
            
        if not data.get('full_name'):
            raise serializers.ValidationError({
                'full_name': 'Full name is required.'
            })
            
        if not data.get('password'):
            raise serializers.ValidationError({
                'password': 'Password is required.'
            })
            
        if not data.get('confirmPassword'):
            raise serializers.ValidationError({
                'confirmPassword': 'Password confirmation is required.'
            })
            
        if data.get('password') != data.get('confirmPassword'):
            raise serializers.ValidationError({
                'confirmPassword': 'Passwords do not match.'
            })
            
        return data
    
    def create(self, validated_data):
        """Create a new user."""
        try:
            # Remove confirmPassword from validated_data
            validated_data.pop('confirmPassword')
            
            # Normalize data
            validated_data['email'] = validated_data['email'].lower().strip()
            validated_data['full_name'] = validated_data['full_name'].strip()
            
            # Create user
            user = User.objects.create_user(**validated_data)
            return user
            
        except ValueError as e:
            raise serializers.ValidationError({
                'detail': str(e)
            })
        except Exception as e:
            raise serializers.ValidationError({
                'detail': f'Failed to create user: {str(e)}'
            })


class LoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    email = serializers.EmailField(
        required=True,
        error_messages={
            'required': 'Email is required.',
            'invalid': 'Please enter a valid email address.',
            'blank': 'Email cannot be blank.'
        }
    )
    password = serializers.CharField(
        required=True,
        error_messages={
            'required': 'Password is required.',
            'blank': 'Password cannot be blank.'
        }
    )
    mfa_code = serializers.CharField(
        required=False,
        allow_blank=True,
        error_messages={
            'invalid': 'Please enter a valid MFA code.'
        }
    )

    def validate_email(self, value):
        """Convert email to lowercase and strip whitespace."""
        return value.lower().strip()


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for password change."""
    old_password = serializers.CharField(
        required=True,
        error_messages={
            'required': 'Current password is required.',
            'blank': 'Current password cannot be blank.'
        }
    )
    new_password = serializers.CharField(
        required=True,
        error_messages={
            'required': 'New password is required.',
            'blank': 'New password cannot be blank.'
        }
    )
    new_password2 = serializers.CharField(
        required=True,
        error_messages={
            'required': 'Password confirmation is required.',
            'blank': 'Password confirmation cannot be blank.'
        }
    )

    def validate(self, data):
        """Validate the new password."""
        if data['new_password'] != data['new_password2']:
            raise serializers.ValidationError({
                'new_password2': 'New passwords do not match.'
            })
            
        try:
            validate_password(data['new_password'])
        except ValidationError as e:
            raise serializers.ValidationError({
                'new_password': list(e.messages)
            })
            
        return data


class MFATokenSerializer(serializers.Serializer):
    """Serializer for MFA token verification."""
    token = serializers.CharField(
        required=True,
        error_messages={
            'required': 'MFA token is required.',
            'blank': 'MFA token cannot be blank.'
        }
    )
    user_id = serializers.IntegerField(
        required=True,
        error_messages={
            'required': 'User ID is required.',
            'invalid': 'Invalid user ID.'
        }
    ) 