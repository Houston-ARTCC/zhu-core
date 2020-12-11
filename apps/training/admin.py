from django.contrib import admin

from .models import TrainingSession, TrainingRequest


@admin.register(TrainingSession)
class TrainingSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'instructor', 'type', 'level', 'status')


@admin.register(TrainingRequest)
class TrainingRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'type', 'level')
