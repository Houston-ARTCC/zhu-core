from django.contrib import admin

from .models import Event, EventPosition, EventPositionRequest


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'host', 'start', 'end', 'hidden')


@admin.register(EventPosition)
class EventPositionAdmin(admin.ModelAdmin):
    list_display = ('callsign', 'event', 'user')


@admin.register(EventPositionRequest)
class EventPositionRequestAdmin(admin.ModelAdmin):
    list_display = ('position', 'user')
