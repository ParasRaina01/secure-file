from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.http import FileResponse
from rest_framework import generics, status, permissions, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import action
from .models import EncryptedFile, FileShare, ShareableLink
from .serializers import (
    EncryptedFileSerializer,
    FileShareSerializer,
    ShareableLinkSerializer,
    FileUploadSerializer,
)
from .permissions import IsOwnerOrSharedWith
from .encryption import encrypt_file, decrypt_file
from django.core.exceptions import PermissionDenied
from django.db import models
import secrets


class FileListCreateView(generics.ListCreateAPIView):
    """View for listing and creating files."""
    serializer_class = EncryptedFileSerializer
    parser_classes = (MultiPartParser, FormParser)
    
    def get_queryset(self):
        return (
            EncryptedFile.objects.filter(owner=self.request.user) |
            EncryptedFile.objects.filter(shares__shared_with=self.request.user)
        ).distinct()
    
    def perform_create(self, serializer):
        # Handle file upload and encryption
        upload_serializer = FileUploadSerializer(data=self.request.data)
        upload_serializer.is_valid(raise_exception=True)
        
        file_obj = upload_serializer.validated_data['file']
        encrypted_data, key, iv = encrypt_file(file_obj)
        
        # Save the encrypted file
        serializer.save(
            owner=self.request.user,
            file=encrypted_data,
            encryption_key=key,
            encryption_iv=iv,
            size=file_obj.size,
            mime_type=file_obj.content_type
        )


class FileDetailView(generics.RetrieveUpdateDestroyAPIView):
    """View for retrieving, updating and deleting files."""
    serializer_class = EncryptedFileSerializer
    permission_classes = (IsOwnerOrSharedWith,)
    lookup_field = 'pk'
    
    def get_queryset(self):
        return (
            EncryptedFile.objects.filter(owner=self.request.user) |
            EncryptedFile.objects.filter(shares__shared_with=self.request.user)
        ).distinct()


class FileDownloadView(APIView):
    """View for downloading files."""
    permission_classes = (IsOwnerOrSharedWith,)
    
    def get(self, request, pk):
        file_obj = get_object_or_404(EncryptedFile, pk=pk)
        self.check_object_permissions(request, file_obj)
        
        # Decrypt the file
        decrypted_data = decrypt_file(
            file_obj.file,
            file_obj.encryption_key,
            file_obj.encryption_iv
        )
        
        response = FileResponse(
            decrypted_data,
            content_type=file_obj.mime_type,
            as_attachment=True,
            filename=file_obj.name
        )
        return response


class FileShareCreateView(generics.CreateAPIView):
    """View for sharing files with other users."""
    serializer_class = FileShareSerializer
    
    def perform_create(self, serializer):
        file_obj = get_object_or_404(
            EncryptedFile,
            pk=self.kwargs['pk'],
            owner=self.request.user
        )
        serializer.save(file=file_obj)


class FileShareListView(generics.ListAPIView):
    """View for listing file shares."""
    serializer_class = FileShareSerializer
    
    def get_queryset(self):
        return FileShare.objects.filter(
            file__owner=self.request.user
        )


class FileShareDetailView(generics.RetrieveDestroyAPIView):
    """View for retrieving and deleting file shares."""
    serializer_class = FileShareSerializer
    
    def get_queryset(self):
        return FileShare.objects.filter(
            file__owner=self.request.user
        )


class ShareableLinkCreateView(generics.CreateAPIView):
    """View for creating shareable links."""
    serializer_class = ShareableLinkSerializer
    
    def perform_create(self, serializer):
        file_obj = get_object_or_404(
            EncryptedFile,
            pk=self.kwargs['pk'],
            owner=self.request.user
        )
        serializer.save(file=file_obj, created_by=self.request.user)


class ShareableLinkListView(generics.ListAPIView):
    """View for listing shareable links."""
    serializer_class = ShareableLinkSerializer
    
    def get_queryset(self):
        return ShareableLink.objects.filter(
            created_by=self.request.user
        )


class ShareableLinkDetailView(generics.RetrieveDestroyAPIView):
    """View for retrieving and deleting shareable links."""
    serializer_class = ShareableLinkSerializer
    
    def get_queryset(self):
        return ShareableLink.objects.filter(
            created_by=self.request.user
        )


class PublicFileDownloadView(APIView):
    """View for downloading files via public links."""
    permission_classes = (permissions.AllowAny,)
    
    def post(self, request, token):
        link = get_object_or_404(ShareableLink, id=token)
        
        # Check if link is valid
        if not link.is_valid():
            return Response(
                {'detail': 'This link has expired or reached its access limit.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify password if set
        if link.password:
            password = request.data.get('password')
            if not password or password != link.password:
                return Response(
                    {'detail': 'Invalid password.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Increment access count
        link.access_count += 1
        link.save()
        
        # Decrypt and serve the file
        decrypted_data = decrypt_file(
            link.file.file,
            link.file.encryption_key,
            link.file.encryption_iv
        )
        
        response = FileResponse(
            decrypted_data,
            content_type=link.file.mime_type,
            as_attachment=True,
            filename=link.file.name
        )
        return response


class FileViewSet(viewsets.ModelViewSet):
    serializer_class = EncryptedFileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrSharedWith]

    def get_queryset(self):
        return EncryptedFile.objects.filter(
            models.Q(owner=self.request.user) | 
            models.Q(shared_with=self.request.user)
        ).distinct()

    def perform_create(self, serializer):
        file = self.request.FILES.get('file')
        encryption_key = self.request.POST.get('encryption_key')
        original_type = self.request.POST.get('original_type')
        
        serializer.save(
            owner=self.request.user,
            encryption_key=encryption_key,
            original_type=original_type
        )

    @action(detail=True, methods=['post'])
    def share(self, request, pk=None):
        file = self.get_object()
        user_email = request.data.get('email')
        
        try:
            user = User.objects.get(email=user_email)
        except User.DoesNotExist:
            return Response(
                {'detail': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        if user == request.user:
            return Response(
                {'detail': 'Cannot share with yourself'},
                status=status.HTTP_400_BAD_REQUEST
            )

        file.shared_with.add(user)
        return Response(EncryptedFileSerializer(file).data)

    @action(detail=True, methods=['post'])
    def create_link(self, request, pk=None):
        file = self.get_object()
        expires_in_days = request.data.get('expires_in_days', 7)
        password = request.data.get('password')
        max_downloads = request.data.get('max_downloads')

        expires_at = timezone.now() + timezone.timedelta(days=expires_in_days)
        token = secrets.token_urlsafe(32)

        link = ShareableLink.objects.create(
            file=file,
            created_by=request.user,
            token=token,
            expires_at=expires_at,
            password=password,
            max_downloads=max_downloads
        )

        return Response(ShareableLinkSerializer(link).data)

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        file = self.get_object()
        
        if not request.user.has_perm('files.download_file', file):
            raise PermissionDenied("You don't have permission to download this file")

        response = FileResponse(file.file)
        response['Content-Disposition'] = f'attachment; filename="{file.name}"'
        response['X-Encryption-Key'] = file.encryption_key
        response['X-Original-Type'] = file.original_type
        return response


class FileShareViewSet(viewsets.ModelViewSet):
    serializer_class = FileShareSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FileShare.objects.filter(
            models.Q(file__owner=self.request.user) | 
            models.Q(shared_with=self.request.user)
        ).distinct()

    def perform_create(self, serializer):
        file = get_object_or_404(EncryptedFile, pk=self.request.data.get('file'))
        if file.owner != self.request.user:
            raise PermissionDenied("You don't have permission to share this file")
        serializer.save(shared_by=self.request.user)


class ShareableLinkViewSet(viewsets.ModelViewSet):
    serializer_class = ShareableLinkSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ShareableLink.objects.filter(
            models.Q(file__owner=self.request.user) | 
            models.Q(created_by=self.request.user)
        ).distinct()

    def perform_create(self, serializer):
        file = get_object_or_404(EncryptedFile, pk=self.request.data.get('file'))
        if file.owner != self.request.user:
            raise PermissionDenied("You don't have permission to create a shareable link for this file")
        
        expires_in_days = self.request.data.get('expires_in_days', 7)
        expires_at = timezone.now() + timezone.timedelta(days=expires_in_days)
        token = secrets.token_urlsafe(32)

        serializer.save(
            file=file,
            created_by=self.request.user,
            token=token,
            expires_at=expires_at
        )
