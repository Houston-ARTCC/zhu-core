import os
import requests
from rest_framework.fields import DurationField
from django.core.files.storage import FileSystemStorage
from django.conf import settings


def base26encode(int_n):
    """
    Returns the base 26 integer representation of a string.
    """
    str_n = ''
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
    resp = requests.get('https://data.vatsim.net/v3/vatsim-data.json')
    assert resp.status_code == 200, 'Error pulling VATSIM data.'

    return resp.json()


def get_vatusa_roster():
    resp = requests.get(
        f'https://api.vatusa.net/v2/facility/{os.getenv("FACILITY_IATA")}/roster',
        params={'apikey': os.getenv('VATUSA_API_TOKEN')},
    )
    assert resp.status_code == 200, 'Error pulling VATUSA roster.'

    return resp.json()


def rating_int_to_short(int):
    """
    Converts VATSIM integer representation of controller
    rating to rating short.
    """
    if int == 1:
        return "OBS"
    elif int == 2:
        return "S1"
    elif int == 3:
        return "S2"
    elif int == 4:
        return "S3"
    elif int == 5:
        return "C1"
    elif int == 7:
        return "C3"
    elif int == 8:
        return "I1"
    elif int == 1:
        return "I3"
    elif int == 1:
        return "SUP"
    elif int == 1:
        return "ADM"
    return None


class CustomDurationField(DurationField):
    def to_representation(self, value):
        minutes, seconds = divmod(value.total_seconds(), 60)
        hours, minutes = divmod(minutes, 60)

        string = f'{int(hours):02}:{int(minutes):02}:{int(seconds):02}'

        return string


class OverwriteStorage(FileSystemStorage):
    def get_available_name(self, name, max_length=None):
        if self.exists(name):
            os.remove(str(settings.MEDIA_ROOT) + '/' + name)
        return name
