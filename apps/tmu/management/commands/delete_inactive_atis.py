from datetime import datetime
from django.core.management.base import BaseCommand

from zhu_core.utils import get_vatsim_data
from apps.tmu.models import ATIS


class Command(BaseCommand):
    help = 'Deletes inactive ATIS broadcasts.'

    def handle(self, *args, **options):
        all_atis = {connection.get('callsign'): connection for connection in get_vatsim_data().get('atis')}
        for atis in ATIS.objects.all():
            if atis.facility + '_ATIS' not in all_atis:
                atis.delete()

        print(f'{datetime.now()} :: delete_inactive_atis :: SUCCESS')
