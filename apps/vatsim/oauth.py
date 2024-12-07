import os
from typing import Optional

import requests
from django.conf import settings

from apps.users.models import User


def process_oauth(code: str) -> User:
    resp = requests.post(
        f"{settings.VATSIM_CONNECT_URL}/oauth/token/",
        data={
            "grant_type": "authorization_code",
            "client_id": os.getenv("VATSIM_CONNECT_CLIENT_ID"),
            "client_secret": os.getenv("VATSIM_CONNECT_CLIENT_SECRET"),
            "redirect_uri": os.getenv("VATSIM_CONNECT_REDIRECT_URI"),
            "code": code,
        },
    )

    assert resp.status_code == 200, "Error authenticating user."

    auth = resp.json()

    data = (
        requests.get(
            f"{settings.VATSIM_CONNECT_URL}/api/user/",
            headers={
                "Authorization": f"Bearer {auth.get('access_token')}",
                "Accept": "application/json",
            },
        )
        .json()
        .get("data")
    )

    user_query = User.objects.filter(cid=data.get("cid"))
    if not user_query.exists():
        user = User.objects.create_user(
            cid=data.get("cid"),
            email=data.get("personal").get("email"),
            first_name=data.get("personal").get("name_first"),
            last_name=data.get("personal").get("name_last"),
            rating=data.get("vatsim").get("rating").get("short"),
            home_facility=get_home_facility(
                data.get("cid"),
                data.get('vatsim').get('division').get('id'),
            ),
        )
    else:
        user = user_query.first()
        user.home_facility = get_home_facility(
            user.cid,
            data.get('vatsim').get('division').get('id'),
            user.home_facility,
        )
        user.rating = data.get("vatsim").get("rating").get("short")
        user.save()

    if user.home_facility == "ZHU":
        user.set_membership("HC")

    return user

# Get the user's home facility.
# Fallback to existing facility if VATUSA API is down.
def get_home_facility(cid: int, division: str, existing_facility: Optional[str] = None) -> str:
    if division != "USA":
        return f"VAT{division}"

    req = requests.get(f"https://api.vatusa.net/v2/user/{cid}")

    if req.status_code == 404:
        return "VATUSA"

    if req.status_code != 200:
        return existing_facility or "VATUSA"

    return req.json().get("data").get("facility")
