from django.contrib import admin

from .models import *


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'host', 'start', 'end', 'hidden')


@admin.register(EventPosition)
class EventPositionAdmin(admin.ModelAdmin):
    list_display = ('callsign', 'event')


@admin.register(PositionShift)
class PositionShiftAdmin(admin.ModelAdmin):
    list_display = ('position', 'user', 'start', 'end')


@admin.register(ShiftRequest)
class ShiftRequestAdmin(admin.ModelAdmin):
    list_display = ('shift', 'user')


@admin.register(SupportRequest)
class SupportRequestAdmin(admin.ModelAdmin):
    list_display = ('name', 'host', 'start', 'end')


@admin.register(PositionPreset)
class PositionPresetAdmin(admin.ModelAdmin):
    list_display = ('name', 'positions')
