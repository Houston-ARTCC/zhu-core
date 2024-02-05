from django.contrib import admin

from .models import LOA


@admin.register(LOA)
class LoaAdmin(admin.ModelAdmin):
    list_display = ("user", "start", "end", "approved")
