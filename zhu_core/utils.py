import os

import requests
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from rest_framework.fields import DurationField


def base26encode(int_n):
    """
    Returns the base 26 integer representation of a string.
    """
    str_n = ""
    while int_n > 25:
        int_n, r = divmod(int_n, 26)
        str_n = chr(r + 65) + str_n
    str_n = chr(int_n + 65) + str_n
    return str_n


def base26decode(str_n):
    """
    Returns the string representation of a base 26 integer.
    """
    int_n = 0
    for pos, char in enumerate(str_n):
        int_n += (ord(char) - 65) * (26 ** (len(str_n) - pos - 1))
    return int_n


def get_vatsim_data():
    resp = requests.get("https://data.vatsim.net/v3/vatsim-data.json")
    assert resp.status_code == 200, "Error pulling VATSIM data."

    return resp.json()


def get_vatusa_roster(membership="home"):
    resp = requests.get(
        f"https://api.vatusa.net/v2/facility/ZHU/roster/{membership}",
        params={"apikey": os.getenv("VATUSA_API_TOKEN")},
    )
    assert resp.status_code == 200, "Error pulling VATUSA roster."

    return resp.json().get("data")


def rating_int_to_short(rating_int):
    """
    Converts VATSIM integer representation of controller
    rating to rating short.
    """
    if rating_int == 1:
        return "OBS"
    elif rating_int == 2:
        return "S1"
    elif rating_int == 3:
        return "S2"
    elif rating_int == 4:
        return "S3"
    elif rating_int == 5:
        return "C1"
    elif rating_int == 7:
        return "C3"
    elif rating_int == 8:
        return "I1"
    elif rating_int == 10:
        return "I3"
    elif rating_int == 11:
        return "SUP"
    elif rating_int == 12:
        return "ADM"
    return ""


class CustomDurationField(DurationField):
    def to_representation(self, value):
        minutes = value.total_seconds() // 60
        hours, minutes = divmod(minutes, 60)

        return f"{int(hours):02}:{int(minutes):02}"


class OverwriteStorage(FileSystemStorage):
    def get_available_name(self, name, max_length=None):
        if self.exists(name):
            os.remove(str(settings.MEDIA_ROOT) + "/" + name)
        return name
