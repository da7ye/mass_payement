from rest_framework import permissions

class IsAccountOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an account to access it
    """
    def has_object_permission(self, request, view, obj):
        # In a real app, this would check the authenticated user
        # For simplicity in this example, we'll allow all requests
        return True