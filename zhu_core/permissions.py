from rest_framework.permissions import BasePermission


class IsMember(BasePermission):
    def has_permission(self, request, view):
        return request.user.roles.filter(short__in=['HC', 'VC', 'MC']).exists()


class IsTrainingStaff(BasePermission):
    def has_permission(self, request, view):
        return request.user.roles.filter(short__in=['INS', 'MTR']).exists()


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.roles.filter(short__in=['ATM', 'DATM', 'WM']).exists()


class IsStaff(BasePermission):
    def has_permission(self, request, view):
        return request.user.roles.filter(
            short__in=['ATM', 'DATM', 'TA', 'ATA', 'FE', 'AFE', 'EC', 'AEC', 'WM', 'AWM']
        ).exists()
