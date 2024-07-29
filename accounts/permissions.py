from rest_framework import permissions

class CustomPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if (request.method in permissions.SAFE_METHODS and request.user and request.user.is_staff) or\
        (request.method in ('POST', 'PATCH') and request.user and request.user.is_authenticated):
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if obj.user_id == request.user.id or request.user.is_staff:
            return True
        return False