import os
import pytz
import requests
from datetime import datetime
from django.core.management.base import BaseCommand

from apps.tmu.models import METAR


class Command(BaseCommand):
    help = 'Fetches the most recent METARs for all stations.'

    def handle(self, *args, **options):
        if os.getenv('AVWX_API_TOKEN') is None:
            return

        airports_iata = os.getenv('POSITION_PREFIXES').split(',')
        airports_icao = ['K' + iata for iata in airports_iata]

        headers = {'Authorization': os.getenv('AVWX_API_TOKEN')}

        for airport in airports_icao:
            url = 'https://avwx.rest/api/metar/' + airport + '?format=json&onfail=cache'
            resp = requests.get(url, headers=headers)
            if resp.status_code == 200:
                data = resp.json()

                METAR.objects.update_or_create(
                    station=airport,
                    defaults={
                        'raw': data.get('sanitized'),
                        'flight_rules': data.get('flight_rules'),
                        'timestamp': pytz.utc.localize(datetime.fromisoformat(data.get('meta').get('timestamp')[:-1])),
                    }
                )
