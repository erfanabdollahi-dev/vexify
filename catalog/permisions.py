from rest_framework import  permissions

class IsAdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return  request.user and request.user.is_staff


from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsOwnerOrAdminOrReadOnly(BasePermission):
    """
    Only the owner of the object can edit it. Others can read.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.user == request.user or request.user.is_staff
