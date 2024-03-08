from django.apps import AppConfig
from django.db.models.signals import m2m_changed


class UserConfig(AppConfig):
    name = "apps.users"

    def ready(self):
        # This needs to be imported here or else the app registry complains that apps aren't loaded yet
        from .models import User
        from .signals import user_roles_changed

        m2m_changed.connect(user_roles_changed, sender=User.roles.through)
