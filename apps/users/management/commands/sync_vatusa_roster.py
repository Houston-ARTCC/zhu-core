import os
from datetime import datetime

import requests
from django.core.management.base import BaseCommand

from zhu_core.utils import get_vatusa_roster
from apps.users.models import User


def sync_home_roster():
    home_roster = get_vatusa_roster()

    # Checks for users that do not exist on local roster.
    for user in home_roster:
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
    cids = [user.get('cid') for user in home_roster]
    for user in User.objects.filter(roles__short='HC'):
        if user.cid not in cids:
            user.set_membership(None)


def sync_visit_roster():
    visit_roster = get_vatusa_roster('visit')
    remote_cids = {user['cid'] for user in visit_roster}

    # Users that have been added to the local roster but not the VATUSA roster.
    for local_cid in User.objects.filter(roles__short='VC').values_list('cid', flat=True):
        if local_cid not in remote_cids:
            requests.post(
                f'https://api.vatusa.net/v2/facility/{os.getenv("FACILITY_IATA")}/roster/manageVisitor/{local_cid}/',
                params={'apikey': os.getenv('VATUSA_API_TOKEN')},
            )


class Command(BaseCommand):
    help = 'Pulls VATUSA roster for configured facility'

    def handle(self, *args, **options):
        sync_home_roster()
        sync_visit_roster()

        print(f'{datetime.now()} :: sync_vatusa_roster :: SUCCESS')
