from django.contrib import admin

from .models import OnlineController, ControllerSession


@admin.register(OnlineController)
class OnlineControllerAdmin(admin.ModelAdmin):
    list_display = ('callsign', 'user', 'online_since', 'last_updated')


@admin.register(ControllerSession)
class ControllerSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'callsign', 'start', 'duration')
