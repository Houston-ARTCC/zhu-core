from rest_framework.permissions import BasePermission, SAFE_METHODS


class ReadOnly(BasePermission):
    """
    Allows access only via SAFE_METHODS.
    """
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class IsOwner(BasePermission):
    """
    Allows access to users who match the 'user' field on the object.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return request.user and obj.user == request.user


class IsMember(BasePermission):
    """
    Allows access to active controllers.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_member


class IsTrainingStaff(BasePermission):
    """
    Allows access to all ARTCC training staff.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_training_staff


class IsStaff(BasePermission):
    """
    Allows access to all ARTCC staff and their assistants.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_staff


class IsAdmin(BasePermission):
    """
    Allows access to ARTCC administrators (ATM, DATM, WM).
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_admin
