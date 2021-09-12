import requests
from datetime import datetime
from django.core.management.base import BaseCommand

from zhu_core.utils import rating_int_to_short
from apps.users.models import Status, User


class Command(BaseCommand):
    help = 'Updates ratings for all active controllers'

    def handle(self, *args, **options):
        for user in User.objects.exclude(status=Status.NON_MEMBER):
            vatsim_data = requests.get('https://api.vatsim.net/api/ratings/' + str(user.cid)).json()

            rating_short = rating_int_to_short(vatsim_data.get('rating'))
            if rating_short:
                user.rating = rating_short
                user.save()

        print(f'{datetime.now()} :: update_user_ratings :: SUCCESS')
