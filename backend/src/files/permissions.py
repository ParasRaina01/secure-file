from rest_framework import permissions


class IsOwnerOrSharedWith(permissions.BasePermission):
    """
    Custom permission to only allow owners of a file or users it's shared with to access it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Write permissions are only allowed to the owner
        if request.method in permissions.SAFE_METHODS:
            return (
                obj.owner == request.user or
                obj.shares.filter(shared_with=request.user).exists()
            )
        
        # For write operations, check if user has write permission
        return (
            obj.owner == request.user or
            obj.shares.filter(
                shared_with=request.user,
                can_write=True
            ).exists()
        ) 