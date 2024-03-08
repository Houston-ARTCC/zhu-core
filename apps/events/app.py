from django.apps import AppConfig
from django.db.models.signals import post_save, pre_save

from .signals import event_webhook_created, event_webhook_edited


class EventsConfig(AppConfig):
    name = "apps.events"

    def ready(self):
        pre_save.connect(event_webhook_edited)
        post_save.connect(event_webhook_created)
