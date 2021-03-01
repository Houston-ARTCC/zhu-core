import requests

from zhu_core.utils import get_vatusa_roster, rating_int_to_short
from .models import User, Status


def sync_vatusa_roster():
    """
    This job pulls all the facility roster from VATUSA
    and syncs with the local roster.
    """
    vatusa_roster = {user.get('cid'): user for user in get_vatusa_roster().values() if type(user) == dict}

    # Checks for users that do not exist on local roster.
    for cid, user in vatusa_roster.items():
        query = User.objects.filter(cid=cid)
        if not query.exists():
            User.objects.create_user(
                cid=cid,
                email=user.get('email'),
                first_name=user.get('fname'),
                last_name=user.get('lname'),
                rating=user.get('rating_short'),
            ).set_membership('HC')
        else:
            user_obj = query.first()
            user_obj.set_membership('HC')
            user_obj.rating = user.get('rating_short')
            user_obj.save()

    # Checks for users that were removed from VATUSA roster.
    for user in User.objects.filter(roles__short='HC'):
        if user.cid not in vatusa_roster:
            user.set_membership(None)


def update_user_ratings():
    """
    This job updates ratings for all active controllers.
    """
    for user in User.objects.exclude(status=Status.NON_MEMBER):
        vatsim_data = requests.get('https://api.vatsim.net/api/ratings/' + str(user.cid)).json()

        rating_short = rating_int_to_short(vatsim_data.get('rating'))
        if rating_short:
            user.rating = rating_short
            user.save()
