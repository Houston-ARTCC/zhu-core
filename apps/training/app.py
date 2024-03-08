from django.apps import AppConfig
from django.db.models.signals import pre_save


class TrainingConfig(AppConfig):
    name = "apps.training"

    def ready(self):
        # This needs to be imported here or else the app registry complains that apps aren't loaded yet
        from .models import TrainingSession
        from .signals import update_ctrs

        pre_save.connect(update_ctrs, sender=TrainingSession)
