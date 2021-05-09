from auditlog.models import LogEntry
from rest_framework.response import Response
from rest_framework.views import APIView

from zhu_core.permissions import IsStaff
from .serializers import LogEntrySerializer
from ..events.models import SupportRequest
from ..feedback.models import Feedback
from ..visit.models import VisitingApplication


class NotificationView(APIView):
    permission_classes = [IsStaff]

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


class AuditLogView(APIView):
    permission_classes = [IsStaff]

    def get(self, request):
        """
        Get list of audit log entries.
        """
        entries = LogEntry.objects.all()
        serializer = LogEntrySerializer(entries, many=True)
        return Response(serializer.data)
