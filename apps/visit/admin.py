from django.contrib import admin

from .models import VisitingApplication


@admin.register(VisitingApplication)
class VisitingApplicationAdmin(admin.ModelAdmin):
    list_display = ("user", "submitted")
