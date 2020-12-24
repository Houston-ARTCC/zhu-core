from django.apps import AppConfig


class UserAppConfig(AppConfig):
    name = 'apps.users'

    def ready(self):
        from zhu_core.scheduler import start_scheduler
        start_scheduler()
