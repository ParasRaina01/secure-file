from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, MFABackupCode


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom admin interface for User model."""
    list_display = ('email', 'full_name', 'is_staff', 'mfa_enabled')
    list_filter = ('is_staff', 'is_superuser', 'mfa_enabled', 'is_active')
    search_fields = ('email', 'full_name')
    ordering = ('email',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('full_name',)}),
        (_('MFA'), {'fields': ('mfa_enabled', 'mfa_secret')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'password1', 'password2'),
        }),
    )


@admin.register(MFABackupCode)
class MFABackupCodeAdmin(admin.ModelAdmin):
    """Admin interface for MFABackupCode model."""
    list_display = ('user', 'used', 'created_at', 'used_at')
    list_filter = ('used', 'created_at', 'used_at')
    search_fields = ('user__email', 'user__full_name')
    readonly_fields = ('created_at', 'used_at')
