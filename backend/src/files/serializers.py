from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import EncryptedFile, FileShare, ShareableLink

User = get_user_model()


class FileUploadSerializer(serializers.Serializer):
    """Serializer for file upload."""
    file = serializers.FileField()


class EncryptedFileSerializer(serializers.ModelSerializer):
    """Serializer for encrypted files."""
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    shared_with = serializers.SerializerMethodField()
    
    class Meta:
        model = EncryptedFile
        fields = (
            'id', 'name', 'owner_username', 'mime_type',
            'size', 'created_at', 'updated_at', 'shared_with'
        )
        read_only_fields = (
            'id', 'owner_username', 'mime_type', 'size',
            'created_at', 'updated_at', 'shared_with'
        )
    
    def get_shared_with(self, obj):
        shares = obj.shares.all()
        return [
            {
                'user': share.shared_with.username,
                'can_write': share.can_write
            }
            for share in shares
        ]


class FileShareSerializer(serializers.ModelSerializer):
    """Serializer for file sharing."""
    shared_with_username = serializers.CharField(write_only=True)
    shared_with_email = serializers.EmailField(write_only=True, required=False)
    
    class Meta:
        model = FileShare
        fields = (
            'id', 'file', 'shared_with', 'can_write',
            'created_at', 'shared_with_username', 'shared_with_email'
        )
        read_only_fields = ('id', 'file', 'created_at')
    
    def validate(self, attrs):
        username = attrs.pop('shared_with_username', None)
        email = attrs.pop('shared_with_email', None)
        
        try:
            if email:
                shared_with = User.objects.get(email=email)
            else:
                shared_with = User.objects.get(username=username)
            
            # Can't share with yourself
            if shared_with == self.context['request'].user:
                raise serializers.ValidationError(
                    'You cannot share a file with yourself.'
                )
            
            attrs['shared_with'] = shared_with
            return attrs
            
        except User.DoesNotExist:
            raise serializers.ValidationError(
                'User not found with the provided username or email.'
            )


class ShareableLinkSerializer(serializers.ModelSerializer):
    """Serializer for shareable links."""
    url = serializers.SerializerMethodField()
    
    class Meta:
        model = ShareableLink
        fields = (
            'id', 'file', 'expires_at', 'password',
            'access_count', 'max_access_count', 'created_at',
            'url'
        )
        read_only_fields = ('id', 'file', 'created_at', 'access_count')
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def get_url(self, obj):
        request = self.context.get('request')
        if request is None:
            return None
        return request.build_absolute_uri(f'/api/files/public/{obj.id}/') 