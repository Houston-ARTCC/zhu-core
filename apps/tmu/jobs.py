import os
from datetime import datetime

import pytz
import requests

from zhu_core.utils import get_vatsim_data
from .models import ATIS, METAR


def delete_inactive_atis():
    """
    This job deletes any ATIS broadcasts from
    vATIS if they are no longer online.
    """
    all_atis = {connection.get('callsign'): connection for connection in get_vatsim_data().get('atis')}
    for atis in ATIS.objects.all():
        if atis.facility + '_ATIS' not in all_atis:
            atis.delete()


def fetch_metars():
    """
    This job fetches the most recent METARs for
    all stations.
    """
    airports_iata = os.getenv('POSITION_PREFIXES').split(',')
    airports_icao = ['K' + iata for iata in airports_iata]

    headers = {'Authorization': os.getenv('AVWX_API_TOKEN')}

    for airport in airports_icao:
        url = 'https://avwx.rest/api/metar/' + airport + '?format=json&onfail=cache'
        resp = requests.get(url, headers=headers)
        data = resp.json()

        query = METAR.objects.filter(station=airport)
        if query.exists():
            query.delete()

        METAR(
            raw=data.get('sanitized'),
            flight_rules=data.get('flight_rules'),
            timestamp=pytz.utc.localize(datetime.fromisoformat(data.get('time').get('dt')[:-1])),
        ).save()
