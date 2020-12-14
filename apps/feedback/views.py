from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from zhu_core.permissions import ReadOnly, IsSeniorStaff
from .models import Feedback
from .serializers import FeedbackSerializer


class FeedbackListView(APIView):
    permission_classes = [ReadOnly | IsAuthenticated]

    def get(self, request, format=None):
        """
        Get list of all feedback.
        """
        feedback = Feedback.objects.all()
        serializer = FeedbackSerializer(feedback, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        """
        Add a new feedback.
        """
        serializer = FeedbackSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FeedbackInstanceView(APIView):
    permission_classes = [IsSeniorStaff]

    def put(self, request, feedback_id, format=None):
        """
        Approve feedback.
        """
        feedback = get_object_or_404(Feedback, id=feedback_id)
        feedback.approved = True
        feedback.save()

    def delete(self, request, feedback_id, format=None):
        """
        Reject feedback.
        """
        feedback = get_object_or_404(Feedback, id=feedback_id)
        feedback.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# TODO: Send email on reception/acception/rejection of feedback.
