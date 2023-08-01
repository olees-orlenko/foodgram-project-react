from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAuthorOrAdminOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or obj.author == request.user

    def has_permission(self, request, view):
        return (request.user.is_authenticated or request.method
                in SAFE_METHODS)
