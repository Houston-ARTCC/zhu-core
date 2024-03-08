from django.apps import AppConfig
from django.db.models.signals import post_save, pre_save


class EventsConfig(AppConfig):
    name = "apps.events"

    def ready(self):
        # This needs to be imported here or else the app registry complains that apps aren't loaded yet
        from .models import Event
        from .signals import event_webhook_created, event_webhook_edited

        pre_save.connect(event_webhook_edited, sender=Event)
        post_save.connect(event_webhook_created, sender=Event)
