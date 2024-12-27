import os
import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.utils import timezone


def get_file_path(instance, filename):
    """Generate a unique path for the uploaded file."""
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'
    return os.path.join('encrypted_files', filename)


class EncryptedFile(models.Model):
    """Model for storing encrypted files."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_files'
    )
    name = models.CharField(_('File name'), max_length=255)
    file = models.FileField(upload_to=get_file_path)
    mime_type = models.CharField(max_length=127)
    size = models.BigIntegerField(
        validators=[MinValueValidator(0)],
        help_text=_('File size in bytes')
    )
    encryption_key = models.BinaryField(
        help_text=_('Encrypted file key')
    )
    encryption_iv = models.BinaryField(
        help_text=_('Initialization vector used for encryption')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('encrypted file')
        verbose_name_plural = _('encrypted files')
        ordering = ['-created_at']
        
    def __str__(self):
        return self.name


class FileShare(models.Model):
    """Model for managing file sharing between users."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.ForeignKey(
        EncryptedFile,
        on_delete=models.CASCADE,
        related_name='shares'
    )
    shared_with = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='shared_files'
    )
    can_write = models.BooleanField(
        default=False,
        help_text=_('Whether the user can modify the file')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('file share')
        verbose_name_plural = _('file shares')
        unique_together = ['file', 'shared_with']
        
    def __str__(self):
        return f'{self.file.name} shared with {self.shared_with}'


class ShareableLink(models.Model):
    """Model for public shareable links."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.ForeignKey(
        EncryptedFile,
        on_delete=models.CASCADE,
        related_name='shareable_links'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_links'
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_('When this link will expire')
    )
    password = models.CharField(
        max_length=128,
        null=True,
        blank=True,
        help_text=_('Optional password protection')
    )
    access_count = models.PositiveIntegerField(
        default=0,
        help_text=_('Number of times this link has been accessed')
    )
    max_access_count = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text=_('Maximum number of times this link can be accessed')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('shareable link')
        verbose_name_plural = _('shareable links')
        
    def __str__(self):
        return f'Share link for {self.file.name}'
        
    def is_valid(self):
        """Check if the link is still valid."""
        if self.expires_at and timezone.now() >= self.expires_at:
            return False
        if self.max_access_count and self.access_count >= self.max_access_count:
            return False
        return True
