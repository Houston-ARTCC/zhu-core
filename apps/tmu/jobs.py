from zhu_core.utils import get_vatsim_data
from .models import ATIS


def delete_inactive_atis():
    """
    This job deletes any ATIS broadcasts from
    vATIS if they are no longer online.
    """
    all_atis = {connection.get('callsign'): connection for connection in get_vatsim_data().get('atis')}
    for atis in ATIS.objects.all():
        if atis.facility + '_ATIS' not in all_atis:
            atis.delete()
