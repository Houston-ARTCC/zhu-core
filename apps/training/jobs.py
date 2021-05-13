from django.utils import timezone

from apps.training.models import TrainingRequest


def clear_expired_requests():
    """
    This job clears expired training requests.
    """
    TrainingRequest.objects.filter(end__lte=timezone.now()).delete()
