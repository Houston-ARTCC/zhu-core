import os
import requests
from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import TrainingSession, Status, Level


def get_default_position(intance):
    if intance.level == Level.MINOR_GROUND:
        return 'AUS_GND'
    if intance.level == Level.MAJOR_GROUND:
        return 'IAH_GND'
    if intance.level == Level.MINOR_TOWER:
        return 'AUS_TWR'
    if intance.level == Level.MAJOR_TOWER:
        return 'IAH_TWR'
    if intance.level == Level.MINOR_APPROACH:
        return 'AUS_APP'
    if intance.level == Level.MAJOR_APPROACH:
        return 'IAH_APP'
    if intance.level == Level.CENTER:
        return 'HOU_CTR'
    if intance.level == Level.OCEANIC:
        return 'ZHU_FSS'


@receiver(pre_save, sender=TrainingSession)
def update_ctrs(instance, **kwargs):
    """
    This signal ensures that training sessions remain synced
    with the VATUSA Centralized Training Record System.
    """
    if instance.status != Status.COMPLETED or instance.level == Level.OCEANIC:
        return

    hours, remainder = divmod(instance.duration.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)

    data = {
        'apikey': os.getenv('VATUSA_API_TOKEN'),
        'instructor_id': instance.instructor.cid,
        'session_date': instance.start.strftime('%Y-%m-%d %H:%M'),
        'position': instance.position if instance.position else get_default_position(instance),
        'duration': f'{int(hours):02}:{int(minutes):02}',
        'movements': instance.movements,
        'score': instance.progress,
        'notes': 'No notes provided.' if instance.notes == '' else instance.notes,
        'location': 1 if instance.type == 2 else 2 if instance.type == 1 else 0,
        'ots_status': instance.ots_status,
    }

    if instance.ctrs_id is not None:
        requests.put(f'https://api.vatusa.net/v2/training/record/{instance.ctrs_id}', data=data)
    else:
        response = requests.post(f'https://api.vatusa.net/v2/user/{instance.student.cid}/training/record', data=data)

        if response.status_code != 200:
            instance.ctrs_id = response.json().get('data').get('id')
