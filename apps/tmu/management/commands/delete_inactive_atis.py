from django.core.management.base import BaseCommand

from apps.tmu.models import ATIS
from zhu_core.utils import get_vatsim_data


class Command(BaseCommand):
    help = 'Deletes inactive ATIS broadcasts.'

    def handle(self, *args, **options):
        all_atis = {connection.get('callsign'): connection for connection in get_vatsim_data().get('atis')}
        for atis in ATIS.objects.all():
            if atis.facility + '_ATIS' not in all_atis:
                atis.delete()
