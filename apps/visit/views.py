import os
import requests
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from zhu_core.permissions import IsAdmin, IsGet, CanVisit
from .serializers import *


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
        serializer = BaseVisitingApplicationSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()

            context = {'user': request.user}
            EmailMultiAlternatives(
                subject='We have received your visiting request!',
                to=[request.user.email],
                from_email=os.getenv('EMAIL_ADDRESS'),
                body=render_to_string('visiting_request_received.txt', context=context),
                alternatives=[(render_to_string('visiting_request_received.html', context=context), 'text/html')],
            ).send()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VisitingInstanceView(APIView):
    permission_classes = [IsAdmin]

    def put(self, request, application_id):
        """
        Approve visiting application.
        """
        application = get_object_or_404(VisitingApplication, id=application_id)
        application.user.set_membership('VC')
        requests.post(
            f'https://api.vatusa.net/v2/facility/{os.getenv("FACILITY_IATA")}'
            f'/roster/manageVisitor/{application.user.cid}/'
        )
        application.delete()
        return Response(status=status.HTTP_200_OK)

    def delete(self, request, application_id):
        """
        Reject visiting application.
        """
        application = get_object_or_404(VisitingApplication, id=application_id)

        context = {'user': application.user, 'reason': request.data.get('reason')}
        EmailMultiAlternatives(
            subject='An update on your visiting request.',
            to=[application.user.email],
            from_email=os.getenv('EMAIL_ADDRESS'),
            body=render_to_string('visiting_request_rejected.txt', context=context),
            alternatives=[(render_to_string('visiting_request_rejected.html', context=context), 'text/html')],
        ).send()

        application.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class EligibilityView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Check if authenticated user is eligible to apply as a visiting controller.
        """
        return Response(request.user.visiting_eligibility)
