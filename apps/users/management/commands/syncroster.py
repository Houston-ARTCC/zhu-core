from django.core.management.base import BaseCommand

from ...jobs import sync_vatusa_roster
from ...models import User, Status


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        sync_vatusa_roster()

        users = User.objects.filter(status=Status.ACTIVE).count()
        self.stdout.write(self.style.SUCCESS(f'Successfully synced {users} users with VATUSA roster!'))
