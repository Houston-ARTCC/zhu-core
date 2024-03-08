import os
from datetime import datetime

import pytz
import requests
from django.core.management.base import BaseCommand

from apps.tmu.models import METAR


class Command(BaseCommand):
    help = "Fetches the most recent METARs for all stations"  # noqa: A003

    def handle(self, *args, **options):
        if os.getenv("AVWX_API_TOKEN") is None:
            return

        headers = {"Authorization": os.getenv("AVWX_API_TOKEN")}

        for iata in os.getenv("POSITION_PREFIXES").split(","):
            icao = f"K{iata}"

            resp = requests.get(f"https://avwx.rest/api/metar/{icao}?format=json&onfail=cache", headers=headers)
            if resp.status_code == 200:
                data = resp.json()

                METAR.objects.update_or_create(
                    station=icao,
                    defaults={
                        "raw": data.get("sanitized"),
                        "flight_rules": data.get("flight_rules"),
                        "timestamp": pytz.utc.localize(datetime.fromisoformat(data.get("meta").get("timestamp")[:-1])),
                    },
                )

        print(f"{datetime.now()} :: fetch_metars :: SUCCESS")
