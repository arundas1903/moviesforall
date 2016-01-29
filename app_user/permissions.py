from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.is_staff


# Used for updating and deleting user
class IsAdminOrSameUser(permissions.BasePermission):

    def has_permission(self, request, view):
        user_instance = view.get_object()
        return request.user.is_staff or user_instance == request.user