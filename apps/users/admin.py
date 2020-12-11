from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from apps.users.models import Role, User


@admin.register(User)
class UserAdmin(UserAdmin):
    model = User
    list_display = ('cid', 'email', 'first_name', 'last_name', 'rating')
    search_fields = list_display
    list_filter = list_display
    ordering = ('cid',)
    fieldsets = (
        ('Personal Information', {'fields': ('cid', 'first_name', 'last_name', 'email', 'password', 'rating')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser', 'roles', 'user_permissions')}),
    )


@admin.register(Role)
class UserAdmin(admin.ModelAdmin):
    model = Role
    list_display = ('long', 'short')
