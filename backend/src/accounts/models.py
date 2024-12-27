from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """Custom user manager that uses email as the unique identifier."""

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user."""
        if not email:
            raise ValueError('Email is required.')
        if not extra_fields.get('full_name'):
            raise ValueError('Full name is required.')
        if not password:
            raise ValueError('Password is required.')
            
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            **extra_fields
        )
        user.set_password(password)
        
        try:
            user.save(using=self._db)
            return user
        except Exception as e:
            raise ValueError(f'Failed to create user: {str(e)}')

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
            
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Custom user model with email as the unique identifier."""
    
    username = None  # Remove username field
    email = models.EmailField(
        _('email address'),
        unique=True,
        error_messages={
            'unique': _("A user with that email already exists."),
            'required': _("Email is required."),
            'invalid': _("Please enter a valid email address."),
        }
    )
    full_name = models.CharField(
        _('full name'),
        max_length=255,
        error_messages={
            'required': _("Full name is required."),
            'max_length': _("Full name cannot be longer than %(max_length)d characters."),
        }
    )
    mfa_secret = models.CharField(
        _('MFA Secret'),
        max_length=32,
        blank=True,
        help_text=_('Secret key for TOTP-based MFA')
    )
    mfa_enabled = models.BooleanField(
        _('MFA Enabled'),
        default=False,
        help_text=_('Whether MFA is enabled for this user')
    )
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        
    def __str__(self):
        return self.email
        
    def save(self, *args, **kwargs):
        """Validate and save the user."""
        if not self.email:
            raise ValueError('Email is required.')
        if not self.full_name:
            raise ValueError('Full name is required.')
            
        # Normalize email
        self.email = self.email.lower().strip()
        # Normalize full name
        self.full_name = self.full_name.strip()
        
        super().save(*args, **kwargs)


class MFABackupCode(models.Model):
    """Backup codes for MFA."""
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='backup_codes'
    )
    code = models.CharField(max_length=8)
    used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = _('MFA backup code')
        verbose_name_plural = _('MFA backup codes')
        ordering = ['-created_at']
        
    def __str__(self):
        return f'Backup code for {self.user.email} ({self.code})'
