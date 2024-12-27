from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    path('mfa/enable/', views.EnableMFAView.as_view(), name='enable-mfa'),
    path('mfa/disable/', views.DisableMFAView.as_view(), name='disable-mfa'),
    path('mfa/verify/', views.VerifyMFAView.as_view(), name='verify-mfa'),
    path('mfa/backup-codes/generate/', views.GenerateBackupCodesView.as_view(), name='generate-backup-codes'),
    path('mfa/backup-codes/verify/', views.VerifyBackupCodeView.as_view(), name='verify-backup-code'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
] 