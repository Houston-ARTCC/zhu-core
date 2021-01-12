from django.contrib import admin

from .models import Feedback


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('id', 'controller', 'controller_callsign', 'pilot', 'rating', 'approved')
