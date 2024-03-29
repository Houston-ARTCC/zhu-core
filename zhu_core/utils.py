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
    match rating_int:
        case 1:
            return "OBS"
        case 2:
            return "S1"
        case 3:
            return "S2"
        case 4:
            return "S3"
        case 5:
            return "C1"
        case 7:
            return "C3"
        case 8:
            return "I1"
        case 10:
            return "I3"
        case 11:
            return "SUP"
        case 12:
            return "ADM"
        case _:
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
