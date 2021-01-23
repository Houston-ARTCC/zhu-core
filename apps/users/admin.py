from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from apps.users.models import Role, User


@admin.register(User)
class UserAdmin(UserAdmin):
    model = User
    list_display = ('cid', 'email', 'first_name', 'last_name', 'rating', 'status')
    search_fields = list_display
    list_filter = ('rating', 'status', 'roles')
    ordering = ('cid',)
    fieldsets = (
        ('Personal Information', {'fields': ('cid', 'first_name', 'last_name', 'email', 'password')}),
        ('Profile', {'fields': ('profile', 'biography')}),
        ('VATSIM Details', {'fields': ('rating', 'home_facility', 'roles', 'status', 'initials')}),
        ('Certifications', {'fields': ('del_cert', 'gnd_cert', 'twr_cert', 'app_cert', 'ctr_cert', 'ocn_cert')}),
        ('Permissions', {'fields': ('is_superuser', 'user_permissions')}),
    )


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    model = Role
    list_display = ('long', 'short')
