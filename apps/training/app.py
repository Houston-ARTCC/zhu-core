from django.apps import AppConfig
from django.db.models.signals import pre_save

from .signals import update_ctrs


class TrainingConfig(AppConfig):
    name = "apps.training"

    def ready(self):
        pre_save.connect(update_ctrs)
