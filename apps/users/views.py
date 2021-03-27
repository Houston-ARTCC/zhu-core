import requests
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from zhu_core.permissions import ReadOnly, IsStaff, IsController, IsTrainingStaff
from zhu_core.utils import rating_int_to_short
from .models import Status
from .serializers import *
from ..feedback.models import Feedback
from ..feedback.serializers import FeedbackSerializer


class ActiveUserListView(APIView):
    def get(self, request):
        """
        Get list of all active users sorted by first name.
        """
        users = User.objects.filter(status=Status.ACTIVE).order_by('first_name')
        if request.user.is_authenticated and request.user.is_staff:
            serializer = AuthenticatedUserSerializer(users, many=True)
        else:
            serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


class UserInstanceView(APIView):
    permission_classes = [ReadOnly | IsStaff]

    def get(self, request, cid):
        """
        Get user.
        """
        user = get_object_or_404(User, cid=cid)
        if request.user.is_authenticated and request.user.is_staff:
            serializer = AuthenticatedUserSerializer(user)
        else:
            serializer = UserSerializer(user)
        return Response(serializer.data)

    def patch(self, request, cid):
        """
        Modify user.
        """
        user = get_object_or_404(User, cid=cid)
        serializer = AuthenticatedUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserFeedbackView(APIView):
    permission_classes = [IsAuthenticated & (IsController | IsStaff | IsTrainingStaff)]

    def get(self, request, cid):
        """
        Get list of all feedback for user.
        """
        feedback = Feedback.objects.filter(controller__cid=cid).filter(approved=True)
        serializer = FeedbackSerializer(feedback, many=True)
        return Response(serializer.data)


class SimplifiedActiveUserListView(APIView):
    def get(self, request):
        """
        Get list of all active users sorted by first name.
        Only includes basic information (CID, name, initials, profile).
        """
        users = User.objects.filter(status=Status.ACTIVE).order_by('first_name')
        serializer = BaseUserSerializer(users, many=True)
        return Response(serializer.data)


class EventScoreActiveUserListView(APIView):
    permission_classes = [IsStaff]

    def get(self, request):
        """
        Get list of all active users sorted by first name.
        Includes basic information and event score.
        """
        users = User.objects.filter(status=Status.ACTIVE).order_by('first_name')
        serializer = EventScoreUserSerializer(users, many=True)
        return Response(serializer.data)


class AllUserListView(APIView):
    permission_classes = [IsStaff]

    def get(self, request):
        """
        Get list of all users sorted by first name.
        """
        users = User.objects.order_by('first_name')
        serializer = AuthenticatedUserSerializer(users, many=True)
        return Response(serializer.data)


class NewestUserListView(APIView):
    def get(self, request):
        """
        Get list of 3 newest controllers.
        """
        users = User.objects.all().order_by('-joined')[:3]
        serializer = BaseUserSerializer(users, many=True)
        return Response(serializer.data)


class StaffListView(APIView):
    permission_classes = [ReadOnly]

    def get(self, request):
        """
        Get list of ARTCC staff.
        """
        atm = BaseUserSerializer(User.objects.filter(roles__short='ATM').first()).data
        datm = BaseUserSerializer(User.objects.filter(roles__short='DATM').first()).data
        ta = BaseUserSerializer(User.objects.filter(roles__short='TA').first()).data
        fe = BaseUserSerializer(User.objects.filter(roles__short='FE').first()).data
        ec = BaseUserSerializer(User.objects.filter(roles__short='EC').first()).data
        wm = BaseUserSerializer(User.objects.filter(roles__short='WM').first()).data
        return Response({
            'atm': {
                'user': atm if atm.get('cid') else None,
            },
            'datm': {
                'user': datm if datm.get('cid') else None,
            },
            'ta': {
                'user': ta if ta.get('cid') else None,
                'assistants': BaseUserSerializer(User.objects.filter(roles__short='ATA'), many=True).data
            },
            'fe': {
                'user': fe if fe.get('cid') else None,
                'assistants': BaseUserSerializer(User.objects.filter(roles__short='AFE'), many=True).data
            },
            'ec': {
                'user': ec if ec.get('cid') else None,
                'assistants': BaseUserSerializer(User.objects.filter(roles__short='AEC'), many=True).data
            },
            'wm': {
                'user': wm if wm.get('cid') else None,
                'assistants': BaseUserSerializer(User.objects.filter(roles__short='AWM'), many=True).data
            },
            'ins': BaseUserSerializer(User.objects.filter(roles__short='INS'), many=True).data,
            'mtr': BaseUserSerializer(User.objects.filter(roles__short='MTR'), many=True).data,
            'web': BaseUserSerializer(User.objects.filter(roles__short='WEB'), many=True).data,
        })


class RoleListView(APIView):
    def get(self, request):
        """
        Get list of all roles.
        """
        roles = Role.objects.all()
        serializer = RoleSerializer(roles, many=True)
        return Response(serializer.data)
