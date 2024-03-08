from django.apps import AppConfig
from django.db.models.signals import m2m_changed

from .models import User
from .signals import user_roles_changed


class UserConfig(AppConfig):
    name = "apps.users"

    def ready(self):
        m2m_changed.connect(user_roles_changed, sender=User.roles.through)
