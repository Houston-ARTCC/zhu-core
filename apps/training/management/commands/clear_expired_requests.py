from datetime import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.training.models import TrainingRequest


class Command(BaseCommand):
    help = "Clears expired training requests"  # noqa: A003

    def handle(self, *args, **options):
        TrainingRequest.objects.filter(end__lte=timezone.now()).delete()

        print(f"{datetime.now()} :: clear_expired_requests :: SUCCESS")
