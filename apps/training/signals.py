import os
from enum import IntEnum

import requests
import sentry_sdk
from rest_framework.exceptions import APIException

from .models import Status
from .models import Type as SessionType


class CTRSSyncError(APIException):
    status_code = 502
    default_detail = "Could not file the session to VATUSA CTRS. Please try again shortly."
    default_code = "ctrs_sync_failed"


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
    """Sync completed training sessions to VATUSA CTRS."""
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

    try:
        if instance.ctrs_id is not None:
            response = requests.put(
                f"https://api.vatusa.net/v2/training/record/{instance.ctrs_id}",
                data=data,
                timeout=15,
            )
        else:
            response = requests.post(
                f"https://api.vatusa.net/v2/user/{instance.student.cid}/training/record",
                data=data,
                timeout=15,
            )
        response.raise_for_status()
    except requests.RequestException as err:
        sentry_sdk.capture_exception(err)
        raise CTRSSyncError() from err

    if instance.ctrs_id is None:
        try:
            instance.ctrs_id = response.json()["data"]["id"]
        except (ValueError, KeyError, TypeError) as err:
            # Record was filed; only the ID readback failed.
            sentry_sdk.capture_exception(err)
