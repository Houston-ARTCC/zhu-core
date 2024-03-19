import os
from enum import IntEnum

import requests

from .models import Status
from .models import Type as SessionType


class Location(IntEnum):
    Classroom = 0
    Live = 1
    Sweatbox = 2


def session_type_to_location(session_type: SessionType) -> Location:
    match session_type:
        case SessionType.CLASSROOM:
            return Location.Classroom
        case SessionType.SWEATBOX:
            return Location.Sweatbox
        case SessionType.ONLINE:
            return Location.Live
        case SessionType.OTS:
            return Location.Live


def update_ctrs(instance, **kwargs):
    """
    This signal ensures that training sessions remain synced
    with the VATUSA Centralized Training Record System.
    """
    if instance.status != Status.COMPLETED:
        return

    hours, remainder = divmod(instance.duration.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)

    data = {
        "apikey": os.getenv("VATUSA_API_TOKEN"),
        "instructor_id": instance.instructor.cid,
        "session_date": instance.start.strftime("%Y-%m-%d %H:%M"),
        "position": instance.position,
        "duration": f"{int(hours):02}:{int(minutes):02}",
        "movements": instance.movements,
        "score": instance.progress,
        "notes": "No notes provided." if instance.notes == "" else instance.notes,
        "location": session_type_to_location(instance.type),
        "ots_status": instance.ots_status,
    }

    if instance.ctrs_id is not None:
        requests.put(f"https://api.vatusa.net/v2/training/record/{instance.ctrs_id}", data=data)
    else:
        response = requests.post(f"https://api.vatusa.net/v2/user/{instance.student.cid}/training/record", data=data)

        if response.status_code == 200:
            instance.ctrs_id = response.json().get("data").get("id")
