from django.contrib import admin

from .models import Email


@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = ('subject', 'to_email', 'cc_email', 'bcc_email', 'get_status_display', 'last_attempt')
