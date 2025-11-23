from rest_framework import permissions
from accounts.models import Role

class IsStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'profile') and request.user.profile.role == Role.STAFF

class IsApprover(permissions.BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'profile') and request.user.profile.role.startswith('approver')

class IsFinance(permissions.BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'profile') and request.user.profile.role == Role.FINANCE
    
class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'profile') and request.user.profile.role == Role.ADMIN

class IsInRoles(permissions.BasePermission):
    """
    Permission that allows access when the authenticated user's profile.role
    is one of the allowed roles passed to the initializer.
    Instantiate with allowed roles list, e.g. IsInRoles(['staff'])
    """
    def __init__(self, roles):
        self.roles = set(roles)

    def has_permission(self, request, view):
        user = request.user
        role = getattr(getattr(user, "profile", None), "role", None)
        return bool(user and user.is_authenticated and role in self.roles)
