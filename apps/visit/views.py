from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from zhu_core.permissions import IsAdmin, IsMember, ReadOnly
from .serializers import *


class VisitingListView(APIView):
    permission_classes = [(ReadOnly & IsAdmin) | (~ReadOnly & ~IsMember & IsAuthenticated)]

    def get(self, request):
        """
        Get list of all visit applications.
        """
        applications = VisitingApplication.objects.all()
        serializer = VisitingApplicationSerializer(applications, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Submit visit application.
        """
        serializer = BaseVisitingApplicationSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VisitingInstanceView(APIView):
    permission_classes = [IsAdmin]

    def put(self, request, application_id):
        """
        Approve visit application.
        """
        application = get_object_or_404(VisitingApplication, id=application_id)
        application.user.set_membership('VC')
        application.delete()
        return Response(status=status.HTTP_200_OK)

    def delete(self, request, application_id):
        """
        Reject visit application.
        """
        application = get_object_or_404(VisitingApplication, id=application_id)
        application.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# TODO: Return Response() on visit request PUT.
# TODO: Send email on reception/acception/rejection of application.
