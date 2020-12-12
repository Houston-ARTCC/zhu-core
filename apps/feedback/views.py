from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Feedback
from .serializers import FeedbackSerializer


class FeedbackListView(APIView):
    authentication_classes = []

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
