from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from zhu_core.permissions import IsMember, IsTrainingStaff, IsOwner, IsPut, IsStudent
from .models import Status
from .serializers import *


class ScheduledSessionListView(APIView):
    permission_classes = [IsTrainingStaff]

    def get(self, request):
        """
        Get list of scheduled training sessions.
        """
        sessions = TrainingSession.objects.filter(status=Status.SCHEDULED)
        serializer = TrainingSessionSerializer(sessions, many=True)
        return Response(serializer.data)


class SessionListView(APIView):
    permission_classes = [IsTrainingStaff | IsStudent]

    def get(self, request, cid):
        """
        Get list of user's training sessions.
        """
        sessions = TrainingSession.objects.filter(student__cid=cid)
        serializer = TrainingSessionSerializer(sessions, many=True)
        return Response(serializer.data)


class SessionInstanceView(APIView):
    permission_classes = [IsTrainingStaff | IsStudent]

    def get(self, request, session_id):
        """
        Get training session details.
        """
        session = get_object_or_404(TrainingSession, id=session_id)
        serializer = TrainingSessionSerializer(session)
        return Response(serializer.data)

    def put(self, request, session_id):
        """
        Modify training session details.
        """
        session = get_object_or_404(TrainingSession, id=session_id)
        serializer = TrainingSessionSerializer(session, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TrainingRequestListView(APIView):
    permission_classes = [IsMember]

    def get(self, request):
        """
        Get list of own pending training requests.
        """
        requests = TrainingRequest.objects.filter(user=request.user, end__gt=timezone.now())
        serializer = TrainingRequestSerializer(requests, many=True)
        return Response(data=serializer.data)

    def post(self, request):
        """
        Submit a new training request.
        """
        serializer = TrainingRequestSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PendingTrainingRequestListView(APIView):
    permission_classes = [IsTrainingStaff]

    def get(self, request):
        """
        Get list of all pending training requests.
        """
        requests = TrainingRequest.objects.filter(end__gt=timezone.now())
        serializer = BaseTrainingRequestSerializer(requests, many=True)
        return Response(data=serializer.data)


class TrainingRequestInstanceView(APIView):
    permission_classes = [(IsPut & IsTrainingStaff) | IsOwner]

    def get_object(self, request_id):
        obj = get_object_or_404(TrainingRequest, id=request_id)
        self.check_object_permissions(self.request, obj)
        return obj

    def put(self, request, request_id):
        """
        Accept training request.
        """
        training_request = get_object_or_404(TrainingRequest, id=request_id)
        serializer = BaseTrainingSessionSerializer(
            data={'student': training_request.user.cid, **request.data},
            context={'request': request}
        )
        if serializer.is_valid():
            training_request.delete()
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, request_id):
        """
        Cancel training request.
        """
        training_request = self.get_object(request_id)
        training_request.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MentorHistoryListView(APIView):
    permission_classes = [IsTrainingStaff]

    def get(self, request, cid):
        """
        Get list of mentor's training sessions.
        """
        sessions = TrainingSession.objects.filter(instructor__cid=cid)
        serializer = TrainingSessionSerializer(sessions, many=True)
        return Response(serializer.data)


class NotificationView(APIView):
    permission_classes = [IsTrainingStaff]

    def get(self, request):
        """
        Returns notification counts for training center categories.
        """
        return Response({
            'training_requests': TrainingRequest.objects.filter(end__gt=timezone.now()).count(),
        })


# TODO: Send email on request received/accepted.
# TODO: Add VATUSA CTRS integration to session PUT.
