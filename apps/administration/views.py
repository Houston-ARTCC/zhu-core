from datetime import date
from auditlog.models import LogEntry
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from zhu_core.permissions import IsStaff
from .serializers import LogEntrySerializer
from ..events.models import SupportRequest
from ..feedback.models import Feedback
from ..loa.models import LOA
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
            'loa_requests': LOA.objects.filter(approved=False).count(),
        })


class AuditLogPagination(PageNumberPagination):
    page_size_query_param = 'page_size'
    page_size = 100


class AuditLogView(ListAPIView):
    permission_classes = [IsStaff]
    pagination_class = AuditLogPagination
    serializer_class = LogEntrySerializer

    def get_queryset(self):
        return LogEntry.objects.all()
