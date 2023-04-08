from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS


class IsAdminForUsers(permissions.BasePermission):

    def has_permission(self, request, view):
        return not request.user.is_anonymous and request.user.is_admin


class IsAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or (
            request.user.is_authenticated and (request.user.is_admin)
        )


class IsAdminModeratorAuthorOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or (
            request.user.is_authenticated
            and (
                request.user == obj.author
                or request.user.is_admin
                or request.user.is_moderator
            )
        )
