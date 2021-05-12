from django.apps import AppConfig


class UserConfig(AppConfig):
    name = 'apps.users'

    def ready(self):
        import apps.users.signals
        from zhu_core.scheduler import start_scheduler
        start_scheduler()
