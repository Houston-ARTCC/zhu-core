from django.utils import timezone
from django.core.management.base import BaseCommand

from apps.training.models import TrainingRequest


class Command(BaseCommand):
    help = 'Clears expired training requests.'

    def handle(self, *args, **options):
        TrainingRequest.objects.filter(end__lte=timezone.now()).delete()
