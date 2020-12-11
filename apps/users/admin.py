from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from apps.users.models import User


@admin.register(User)
class UserAdmin(UserAdmin):
    model = User
    list_display = ('cid', 'email', 'first_name', 'last_name')
    list_filter = list_display
    fieldsets = (
        ('Personal Information', {'fields': ('cid', 'first_name', 'last_name', 'email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    search_fields = list_display
    ordering = ('cid',)
