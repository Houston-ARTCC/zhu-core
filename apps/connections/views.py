from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import Status, User
from zhu_core.permissions import IsGet, IsMember, IsStaff

from .models import ControllerSession, OnlineController
from .serializers import (
    AdminStatisticsSerializer,
    ControllerSessionSerializer,
    DailyConnectionsSerializer,
    OnlineControllerSerializer,
    StatisticsSerializer,
    StatusStatisticsSerializer,
    TopControllersSerializer,
    TopPositionsSerializer,
)
from .statistics import (
    aggregate_quarterly_hours,
    get_daily_statistics,
    get_top_controllers,
    get_top_positions,
)


class StatisticsView(APIView):
    permission_classes = [IsGet]

    def get(self, request):
        users = User.objects.exclude(status=Status.NON_MEMBER)
        statistics = aggregate_quarterly_hours(users.values("cid")).values(*StatisticsSerializer.Meta.fields)

        return Response(
            {
                "home": StatisticsSerializer(statistics.filter(roles__short="HC"), many=True).data,
                "visiting": StatisticsSerializer(statistics.filter(roles__short="VC"), many=True).data,
            }
        )


class AdminStatisticsView(APIView):
    permission_classes = [IsStaff]

    def get(self, request):
        users = User.objects.exclude(status=Status.NON_MEMBER)
        statistics = aggregate_quarterly_hours(users.values("cid")).values(*AdminStatisticsSerializer.Meta.fields)

        return Response(
            {
                "home": AdminStatisticsSerializer(statistics.filter(roles__short="HC"), many=True).data,
                "visiting": AdminStatisticsSerializer(statistics.filter(roles__short="VC"), many=True).data,
            }
        )


class QuarterlyStatusView(APIView):
    permission_classes = [IsMember]

    def get(self, request):
        """
        Get own quarterly status
        """
        user = User.objects.filter(cid=request.user.cid)
        statistics = aggregate_quarterly_hours(user).values(*StatusStatisticsSerializer.Meta.fields)
        serializer = StatusStatisticsSerializer(statistics.first())
        return Response(serializer.data)


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
