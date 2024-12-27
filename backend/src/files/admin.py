from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import EncryptedFile, FileShare, ShareableLink


@admin.register(EncryptedFile)
class EncryptedFileAdmin(admin.ModelAdmin):
    """Admin interface for EncryptedFile model."""
    list_display = ('name', 'owner', 'mime_type', 'size', 'created_at')
    list_filter = ('mime_type', 'created_at')
    search_fields = ('name', 'owner__username', 'owner__email')
    readonly_fields = ('id', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'


@admin.register(FileShare)
class FileShareAdmin(admin.ModelAdmin):
    """Admin interface for FileShare model."""
    list_display = ('file', 'shared_with', 'can_write', 'created_at')
    list_filter = ('can_write', 'created_at')
    search_fields = ('file__name', 'shared_with__username', 'shared_with__email')
    readonly_fields = ('id', 'created_at')


@admin.register(ShareableLink)
class ShareableLinkAdmin(admin.ModelAdmin):
    """Admin interface for ShareableLink model."""
    list_display = ('file', 'created_by', 'expires_at', 'access_count', 'created_at')
    list_filter = ('created_at', 'expires_at')
    search_fields = ('file__name', 'created_by__username', 'created_by__email')
    readonly_fields = ('id', 'created_at', 'access_count')
    date_hierarchy = 'created_at'
