from django.contrib import admin

from .models import MentorAvailability, TrainingRequest, TrainingSession


@admin.register(TrainingSession)
class TrainingSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "student", "instructor", "type", "level", "status")


@admin.register(TrainingRequest)
class TrainingRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "type", "level")


@admin.register(MentorAvailability)
class MentorAvailabilityAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "day", "start", "end")
