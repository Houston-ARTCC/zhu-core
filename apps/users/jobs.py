from zhu_core.utils import get_vatusa_roster
from .models import User


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
            query.first().set_membership('HC')

    # Checks for users that were removed from VATUSA roster.
    for user in User.objects.filter(roles__short__in=['HC', 'VC', 'MC']):
        if user.cid not in vatusa_roster:
            user.set_membership(None)
