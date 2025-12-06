from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of a task or admins to access it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Admins can access any task
        if request.user.is_admin:
            return True
        
        # Users can only access their own tasks
        return obj.owner == request.user


class IsAdminUser(permissions.BasePermission):
    """
    Custom permission to only allow admin users.
    Checks the custom 'role' field instead of is_staff.
    """
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_admin)