from datetime import timedelta

from django.db.models import DurationField
from django.db.models.aggregates import Sum
from django.db.models.functions import Cast, Coalesce
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import User
from zhu_core.permissions import IsGet, IsStaff

from .models import ControllerSession, OnlineController
from .serializers import (
    ControllerSessionSerializer,
    DailyConnectionsSerializer,
    OnlineControllerSerializer,
    StatisticsSerializer,
    TopControllersSerializer,
    TopPositionsSerializer,
)
from .statistics import get_daily_statistics, get_top_controllers, get_top_positions, get_user_hours


class ControllerSessionsView(APIView):
    permission_classes = [IsGet]

    def get(self, request, cid):
        """
        Get list of all controller's sessions.
        """
        user = get_object_or_404(User, cid=cid)
        sessions = ControllerSession.objects.filter(user=user)
        serializer = ControllerSessionSerializer(sessions, many=True)
        return Response(serializer.data)


class OnlineControllersView(APIView):
    permission_classes = [IsGet]

    def get(self, request):
        """
        Get list of all online controllers.
        """
        controllers = OnlineController.objects.all()
        serializer = OnlineControllerSerializer(controllers, many=True)
        return Response(serializer.data)


class TopControllersView(APIView):
    permission_classes = [IsGet]

    def get(self, request):
        """
        Get list of controllers sorted by most
        hours for the current month.
        """
        controllers = get_top_controllers()
        serializer = TopControllersSerializer(controllers, many=True)
        return Response(serializer.data)


class TopPositionsView(APIView):
    permission_classes = [IsGet]

    def get(self, request):
        """
        Get list of positions sorted by most
        hours for the current month.
        """
        positions = get_top_positions()
        serializer = TopPositionsSerializer(positions, many=True)
        return Response(serializer.data)


class StatisticsView(APIView):
    permission_classes = [IsGet]

    def get(self, request):
        """
        Get list of all controllers along with hours for
        current, previous, and penultimate months.
        Sorted into home, visiting, and mavp controllers.
        """
        hours = get_user_hours()
        return Response(
            {
                "home": StatisticsSerializer(hours.filter(roles__short="HC"), many=True).data,
                "visiting": StatisticsSerializer(hours.filter(roles__short="VC"), many=True).data,
                "mavp": StatisticsSerializer(hours.filter(roles__short="MC"), many=True).data,
            }
        )


class DailyStatisticsView(APIView):
    def get(self, request, year):
        """
        Get list of controlling hours for
        every day of the given year.
        """
        connections = get_daily_statistics(year)
        serializer = DailyConnectionsSerializer(connections, many=True)
        return Response(serializer.data)


class UserDailyStatisticsView(APIView):
    def get(self, request, year, cid):
        """
        Get list of controlling hours for every
        day of the given year for the given user.
        """
        user = get_object_or_404(User, cid=cid)
        connections = get_daily_statistics(year, user)
        serializer = DailyConnectionsSerializer(connections, many=True)
        return Response(serializer.data)


class AdminStatisticsView(APIView):
    permission_classes = [IsStaff]

    def get(self, request):
        """
        Get total hours for the current month and year.
        """
        current_date = timezone.now()
        year_sessions = ControllerSession.objects.filter(start__year=current_date.year)
        month_sessions = year_sessions.filter(start__month=current_date.month)

        SUM_DURATION = Coalesce(Sum("duration"), Cast(timedelta(), DurationField()))

        return Response(
            {
                "month": month_sessions.aggregate(total=SUM_DURATION).get("total").total_seconds(),
                "year": year_sessions.aggregate(total=SUM_DURATION).get("total").total_seconds(),
            }
        )
