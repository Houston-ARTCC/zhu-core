from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from zhu_core.permissions import IsAdmin, IsMember, ReadOnly
from .models import VisitingApplication
from .serializers import VisitingApplicationSerializer


class VisitingListView(APIView):
    permission_classes = [~IsMember | (ReadOnly & IsAdmin)]

    def get(self, request, format=None):
        """
        Get list of all visiting applications.
        """
        feedback = VisitingApplication.objects.all()
        serializer = VisitingApplicationSerializer(feedback, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        """
        Submit visiting application.
        """
        serializer = VisitingApplicationSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VisitingInstanceView(APIView):
    permission_classes = [IsAdmin]

    def put(self, request, application_id, format=None):
        """
        Approve visiting application.
        """
        feedback = get_object_or_404(VisitingApplication, id=application_id)
        feedback.user.set_membership('VC')
        feedback.delete()

    def delete(self, request, application_id, format=None):
        """
        Reject visiting application.
        """
        feedback = get_object_or_404(VisitingApplication, id=application_id)
        feedback.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# TODO: Send email on reception/acception/rejection of application.
