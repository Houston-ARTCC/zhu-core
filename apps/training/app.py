from django.apps import AppConfig


class TrainingConfig(AppConfig):
    name = 'apps.training'

    def ready(self):
        import apps.training.signals
