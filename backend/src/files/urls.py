from django.urls import path
from . import views

app_name = 'files'

urlpatterns = [
    # File Management
    path('', views.FileListCreateView.as_view(), name='file-list'),
    path('<uuid:pk>/', views.FileDetailView.as_view(), name='file-detail'),
    path('<uuid:pk>/download/', views.FileDownloadView.as_view(), name='file-download'),
    
    # File Sharing
    path('<uuid:pk>/share/', views.FileShareCreateView.as_view(), name='file-share'),
    path('shares/', views.FileShareListView.as_view(), name='share-list'),
    path('shares/<uuid:pk>/', views.FileShareDetailView.as_view(), name='share-detail'),
    
    # Shareable Links
    path('<uuid:pk>/create-link/', views.ShareableLinkCreateView.as_view(), name='create-link'),
    path('links/', views.ShareableLinkListView.as_view(), name='link-list'),
    path('links/<uuid:pk>/', views.ShareableLinkDetailView.as_view(), name='link-detail'),
    path('public/<uuid:token>/', views.PublicFileDownloadView.as_view(), name='public-download'),
] 