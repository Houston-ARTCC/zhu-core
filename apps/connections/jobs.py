import os
import pytz
from datetime import datetime

from zhu_core.utils import get_vatsim_data
from .models import OnlineController
from ..users.models import User


def update_online_controllers():
    """
    This job pulls all connections from the VATSIM data API
    and updates all current controlling sessions and creates
    new ones as needed.
    """
    position_prefixes = os.getenv('POSITION_PREFIXES').split(',')
    connections = {connection.get('callsign'): connection for connection in get_vatsim_data().get('controllers')}

    # Updates all controllers currently online.
    for online in OnlineController.objects.all():
        if online.callsign in connections and connections.get(online.callsign).cid == online.user.cid:
            online.save()
        else:
            online.convert_to_session()
            online.delete()

    # Checks for new connections.
    for callsign, connection in connections.items():
        user = User.objects.filter(cid=connection.get('cid'))
        if user.exists() and not OnlineController.objects.filter(callsign=callsign, user=user).exists():
            if callsign.split('_')[0] in position_prefixes and callsign.split('_')[-1] not in ['SUP', 'OBS']:
                OnlineController(
                    user=user.first(),
                    callsign=callsign,
                    online_since=pytz.utc.localize(
                        datetime.strptime(connection.get('logon_time')[:-2], '%Y-%m-%dT%H:%M:%S.%f')
                    )
                ).save()
