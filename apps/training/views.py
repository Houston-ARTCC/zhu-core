from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from zhu_core.permissions import IsMember, IsTrainingStaff, ReadOnly, IsOwner, IsPut, IsStudent
from .serializers import *


class StudentSessionListView(APIView):
    permission_classes = [IsMember]

    def get(self, request):
        """
        Get list of own training sessions.
        """
        sessions = TrainingSession.objects.filter(student=request.user)
        serializer = TrainingSessionSerializer(sessions, many=True)
        return Response(serializer.data)


class SessionListView(APIView):
    permission_classes = [IsTrainingStaff]

    def get(self, request):
        """
        Get list of all training sessions.
        """
        sessions = TrainingSession.objects.all()
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
    permission_classes = [(ReadOnly & IsTrainingStaff) | IsMember]

    def get(self, request):
        """
        Get list of all active training requests.
        """
        requests = TrainingRequest.objects.filter(end__gt=timezone.now())
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


class TrainingRequestInstanceView(APIView):
    permission_classes = [(IsPut & IsTrainingStaff) | IsOwner]

    def put(self, request, request_id):
        """
        Accept training request.
        """
        training_request = get_object_or_404(TrainingRequest, id=request_id)
        training_request.delete()

    def delete(self, request, request_id):
        """
        Cancel training request.
        """
        training_request = get_object_or_404(TrainingRequest, id=request_id)
        self.check_object_permissions(self.request, training_request)
        training_request.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# TODO: Send email on request received/accepted.
# TODO: Add VATUSA CTRS integration to session PUT.
