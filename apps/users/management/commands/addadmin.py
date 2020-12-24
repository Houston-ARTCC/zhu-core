from getpass import getpass
from django.core.management.base import BaseCommand, CommandError

from apps.users.models import User, Role


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        cid = input('CID: ')
        try:
            user = User.objects.get(cid=cid)
        except User.DoesNotExist:
            raise CommandError(f'User with CID {cid} does not exist locally! Have you ran `syncroster`?')

        short = input('Role (ATM, DATM, etc.): ')
        try:
            role = Role.objects.get(short__iexact=short)
        except Role.DoesNotExist:
            raise CommandError(f'Role {short} does not exist!')

        password1 = getpass('Password: ')
        password2 = getpass('Confirm Password: ')

        if password1 != password2:
            raise CommandError('Passwords do not match!')

        user.set_password(password1)
        user.roles.add(role)
        user.is_superuser = True
        user.save()

        self.stdout.write(self.style.SUCCESS(f'User {user.full_name} set as {role.long}!'))
