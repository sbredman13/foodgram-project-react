from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS


class IsAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or (
            request.user.is_authenticated and (request.user.is_admin)
        )


class IsAuthorOrAdminPermission(permissions.BasePermission):
    message = "Только у админа или автора контента есть доступ."

    def has_permission(self, request, view):
        return (
            request.method
            in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_superuser
            or obj.author == request.user
        )
