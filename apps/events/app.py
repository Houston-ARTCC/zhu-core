import os

from django.apps import AppConfig


class EventsConfig(AppConfig):
    name = "apps.events"

    def ready(self):
        if os.getenv("EVENTS_WEBHOOK_URL"):
            pass
