from rest_framework.response import Response
from rest_framework.views import APIView

from apps.events.models import SupportRequest
from apps.feedback.models import Feedback
from apps.visit.models import VisitingApplication


class NotificationListView(APIView):
    def get(self, request):
        """
        Returns notification counts for admin panel categories.
        """
        return Response({
            'visiting_applications': VisitingApplication.objects.count(),
            'pending_feedback': Feedback.objects.filter(approved=False).count(),
            'support_requests': SupportRequest.objects.count(),
            'loa_requests': 0,
        })
