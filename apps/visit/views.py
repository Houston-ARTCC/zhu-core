from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.mailer.models import Email
from zhu_core.permissions import CanVisit, IsAdmin, IsGet

from .models import VisitingApplication
from .serializers import BaseVisitingApplicationSerializer, VisitingApplicationSerializer


class VisitingListView(APIView):
    permission_classes = [(IsGet & IsAdmin) | (~IsGet & IsAuthenticated & CanVisit)]

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
        serializer = BaseVisitingApplicationSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()

            Email.objects.queue(
                to=request.user,
                subject="We have received your visiting request",
                from_email="management@houston.center",
                template="visiting_request_received",
            )

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VisitingInstanceView(APIView):
    permission_classes = [IsAdmin]

    def put(self, request, application_id):
        """
        Approve visiting application.
        """
        application = get_object_or_404(VisitingApplication, id=application_id)
        application.user.set_membership("VC")
        application.delete()
        return Response(status=status.HTTP_200_OK)

    def delete(self, request, application_id):
        """
        Reject visiting application.
        """
        application = get_object_or_404(VisitingApplication, id=application_id)

        Email.objects.queue(
            to=application.user,
            subject="An update on your visiting request",
            from_email="management@houston.center",
            template="visiting_request_rejected",
            context={"reason": request.data.get("reason")},
        )

        application.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class EligibilityView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Check if authenticated user is eligible to apply as a visiting controller.
        """
        return Response(request.user.visiting_eligibility)
