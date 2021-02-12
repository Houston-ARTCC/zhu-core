from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from zhu_core.permissions import IsSeniorStaff, ReadOnly
from .serializers import *


class FeedbackListView(APIView):
    permission_classes = [(ReadOnly & IsSeniorStaff) | (~ReadOnly & IsAuthenticated)]

    def get(self, request):
        """
        Get list of unapproved feedback.
        """
        feedback = Feedback.objects.filter(approved=False)
        serializer = FeedbackSerializer(feedback, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Add a new feedback.
        """
        serializer = FeedbackSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FeedbackInstanceView(APIView):
    permission_classes = [IsSeniorStaff]

    def put(self, request, feedback_id):
        """
        Approve feedback.
        """
        feedback = get_object_or_404(Feedback, id=feedback_id)
        feedback.approved = True
        feedback.save()

    def delete(self, request, feedback_id):
        """
        Reject feedback.
        """
        feedback = get_object_or_404(Feedback, id=feedback_id)
        feedback.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# TODO: Send email on reception/acception/rejection of feedback.
