from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from zhu_core.permissions import ReadOnly
from .serializers import *
from .statistics import *
from ..users.models import User


class ControllerSessionsView(APIView):
    permission_classes = [ReadOnly]

    def get(self, request, cid, format=None):
        """
        Get list of all controller's sessions.
        """
        user = get_object_or_404(User, cid=cid)
        sessions = ControllerSession.objects.filter(user=user)
        serializer = ControllerSessionSerializer(sessions, many=True)
        return Response(serializer.data)


class OnlineControllersView(APIView):
    permission_classes = [ReadOnly]

    def get(self, request, format=None):
        """
        Get list of all online controllers.
        """
        controllers = OnlineController.objects.all()
        serializer = OnlineControllerSerializer(controllers, many=True)
        return Response(serializer.data)


class TopControllersView(APIView):
    permission_classes = [ReadOnly]

    def get(self, request, format=None):
        """
        Get list of controllers sorted by most
        hours for the current month.
        """
        controllers = get_top_controllers()
        serializer = TopControllersSerializer(controllers, many=True)
        return Response(serializer.data)


class TopPositionsView(APIView):
    permission_classes = [ReadOnly]

    def get(self, request, format=None):
        """
        Get list of positions sorted by most
        hours for the current month.
        """
        positions = get_top_positions()
        serializer = TopPositionsSerializer(positions, many=True)
        return Response(serializer.data)


class StatisticsView(APIView):
    permission_classes = [ReadOnly]

    def get(self, request, format=None):
        """
        Get list of all controllers along with hours for
        current, previous, and penultimate months.
        """
        hours = get_user_hours()
        serializer = StatisticsSerializer(hours, many=True)
        return Response(serializer.data)


class DailyStatisticsView(APIView):
    def get(self, request, year, format=None):
        """
        Get list of controlling hours for
        every day of the given year.
        """
        connections = get_daily_statistics(year)
        serializer = DailyConnectionsSerializer(connections, many=True)
        return Response(serializer.data)


class UserDailyStatisticsView(APIView):
    def get(self, request, year, cid, format=None):
        """
        Get list of controlling hours for every
        day of the given year for the given user.
        """
        user = get_object_or_404(User, cid=cid)
        connections = get_daily_statistics(year, user)
        serializer = DailyConnectionsSerializer(connections, many=True)
        return Response(serializer.data)
