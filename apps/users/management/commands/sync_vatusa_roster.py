from datetime import datetime
from django.core.management.base import BaseCommand

from zhu_core.utils import get_vatusa_roster
from apps.users.models import User


class Command(BaseCommand):
    help = 'Pulls VATUSA roster for configured facility'

    def handle(self, *args, **options):
        roster = get_vatusa_roster()

        # Checks for users that do not exist on local roster.
        for user in roster:
            query = User.objects.filter(cid=user.get('cid'))
            if not query.exists():
                User.objects.create_user(
                    cid=user.get('cid'),
                    email=user.get('email'),
                    first_name=user.get('fname'),
                    last_name=user.get('lname'),
                    rating=user.get('rating_short'),
                ).set_membership('HC')
            else:
                user_obj = query.first()
                user_obj.rating = user.get('rating_short')
                user_obj.save()
                user_obj.set_membership('HC')

        # Checks for users that were removed from VATUSA roster.
        cids = [user.get('cid') for user in roster]
        for user in User.objects.filter(roles__short='HC'):
            if user.cid not in cids:
                user.set_membership(None)

        print(f'{datetime.now()} :: sync_vatusa_roster :: SUCCESS')
