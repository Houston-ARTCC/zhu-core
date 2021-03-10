from datetime import datetime
from rest_framework.response import Response
from rest_framework.views import APIView

from zhu_core.permissions import ReadOnly
from .serializers import *
from ..training.models import Status


class EventCalendarView(APIView):
    permission_classes = [ReadOnly]

    def get(self, request, year=datetime.now().year, month=datetime.now().month):
        """
        Get all events for given month and year.
        Defaults to current month of current year.
        """
        events = Event.objects.filter(start__month=month, start__year=year)

        if not (request.user.is_authenticated and request.user.is_staff):
            events = events.exclude(hidden=True)

        serializer = EventCalendarSerializer(events, many=True)
        return Response(serializer.data)


class TrainingCalendarView(APIView):
    permission_classes = [ReadOnly]

    def get(self, request, year=datetime.now().year, month=datetime.now().month):
        """
        Get all training sessions for given month and year.
        Defaults to current month of current year.
        """
        sessions = TrainingSession.objects.filter(start__month=month, start__year=year).exclude(status=Status.CANCELLED)

        serializer = TrainingCalendarSerializer(sessions, many=True)
        return Response(serializer.data)
