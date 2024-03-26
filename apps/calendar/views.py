from datetime import datetime

from rest_framework.response import Response
from rest_framework.views import APIView

from apps.events.models import Event
from apps.training.models import Status, TrainingSession
from zhu_core.permissions import IsGet

from .serializers import CalendarEventSerializer, CalendarTrainingSerializer


class CalendarView(APIView):
    permission_classes = [IsGet]

    def get(self, request, year=datetime.now().year, month=datetime.now().month):
        """
        Get all calendar events for given month and year.
        Defaults to current month of current year.
        {
            'events': [],
            'sessions': [],
        }
        """
        events = Event.objects.filter(start__month=month, start__year=year)
        sessions = TrainingSession.objects.filter(start__month=month, start__year=year).exclude(status=Status.CANCELLED)

        if not (request.user.is_authenticated and request.user.is_staff):
            events = events.exclude(hidden=True)

        event_serializer = CalendarEventSerializer(events, many=True)
        session_serializer = CalendarTrainingSerializer(sessions, many=True)

        return Response(
            {
                "events": event_serializer.data,
                "sessions": session_serializer.data,
            }
        )
