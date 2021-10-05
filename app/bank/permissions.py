from rest_framework.permissions import BasePermission


class IsTeller(BasePermission):
    """
        Permission class to make sure that the current user is the teller of
        the branch
    """
    def has_object_permission(self, request, view, obj):
        return request.user == obj.teller
