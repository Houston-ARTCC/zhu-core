from django.contrib import admin

from .models import ATIS, METAR, TMUNotice


@admin.register(ATIS)
class ATISAdmin(admin.ModelAdmin):
    list_display = ("atis_letter", "facility", "config_profile", "updated")


@admin.register(TMUNotice)
class TMUNoticeAdmin(admin.ModelAdmin):
    list_display = ("info", "time_issued", "time_expires")


@admin.register(METAR)
class METARAdmin(admin.ModelAdmin):
    list_display = ("station", "flight_rules", "raw", "timestamp")
