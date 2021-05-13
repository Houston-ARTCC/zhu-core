import os
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from zhu_core.permissions import IsSeniorStaff, IsGet
from .serializers import *


class FeedbackListView(APIView):
    permission_classes = [(IsGet & IsSeniorStaff) | (~IsGet & IsAuthenticated)]

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
        serializer = BaseFeedbackSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()

            try:
                context = {'user': request.user, 'feedback': serializer.instance}
                EmailMultiAlternatives(
                    subject='We have received your feedback!',
                    to=[request.user.email],
                    from_email=os.getenv('EMAIL_ADDRESS'),
                    body=render_to_string('feedback_received.txt', context=context),
                    alternatives=[(render_to_string('feedback_received.html', context=context), 'text/html')],
                ).send()
            except:
                pass

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

        try:
            context = {'user': feedback.pilot, 'feedback': feedback}
            EmailMultiAlternatives(
                subject='Your feedback has been approved!',
                to=[feedback.pilot.email],
                from_email=os.getenv('EMAIL_ADDRESS'),
                body=render_to_string('feedback_approved.txt', context=context),
                alternatives=[(render_to_string('feedback_approved.html', context=context), 'text/html')],
            ).send()
        except:
            pass

        return Response(status=status.HTTP_200_OK)

    def delete(self, request, feedback_id):
        """
        Reject feedback.
        """
        feedback = get_object_or_404(Feedback, id=feedback_id)
        feedback.delete()

        try:
            context = {'user': feedback.pilot, 'feedback': feedback, 'reason': request.data.get('reason')}
            EmailMultiAlternatives(
                subject='An update on your feedback.',
                to=[feedback.pilot.email],
                from_email=os.getenv('EMAIL_ADDRESS'),
                body=render_to_string('feedback_rejected.txt', context=context),
                alternatives=[(render_to_string('feedback_rejected.html', context=context), 'text/html')],
            ).send()
        except:
            pass

        return Response(status=status.HTTP_204_NO_CONTENT)
