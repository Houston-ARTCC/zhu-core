from rest_framework.permissions import BasePermission, SAFE_METHODS


class ReadOnly(BasePermission):
    """
    Allows access only via SAFE_METHODS.
    """
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class IsOwner(BasePermission):
    """
    Allows access to users who match the 'user' field.
    """
    def has_object_permission(self, request, view, obj):
        return request.user and obj.user == request.user


class IsController(BasePermission):
    """
    Allows access to users who match the 'cid' param via SAFE_METHDOS only.
    """
    def has_permission(self, request, view):
        if request.method not in SAFE_METHODS:
            return False

        return request.user and request.parser_context.get('kwargs').get('cid') == request.user.cid


class IsStudent(BasePermission):
    """
    Allows access to users who match the 'student' field via SAFE_METHDOS only.
    """
    def has_object_permission(self, request, view, obj):
        if request.method not in SAFE_METHODS:
            return False

        return request.user and obj.student == request.user


class IsMember(BasePermission):
    """
    Allows access to active controllers.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_member


class IsTrainingStaff(BasePermission):
    """
    Allows access to ARTCC training staff.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_training_staff


class IsStaff(BasePermission):
    """
    Allows access to ARTCC staff and their assistants.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_staff


class IsSeniorStaff(BasePermission):
    """
    Allows access to the ATM, DATM, and TA.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_senior_staff


class IsAdmin(BasePermission):
    """
    Allows access to the ATM and DATM.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class IsPut(BasePermission):
    """
    Allows access to PUT requests.
    """
    def has_permission(self, request, view):
        return request.method == 'PUT'


class IsDelete(BasePermission):
    """
    Allows access to DELETE requests.
    """
    def has_permission(self, request, view):
        return request.method == 'DELETE'
