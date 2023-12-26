from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.loa.models import LOA
from apps.mailer.models import Email
from zhu_core.permissions import IsAdmin

from .serlaizers import BaseLOASerializer, LOASerializer


class LOARequestListView(APIView):
    permission_classes = []

    def get(self, request):
        """
        Get list of all outstanding LOA requests.
        """
        loas = LOA.objects.filter(approved=False)
        serializer = LOASerializer(loas, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Submit LOA request.
        """
        serializer = BaseLOASerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LOARequestInstanceView(APIView):
    permission_classes = [IsAdmin]

    def put(self, request, request_id):
        """
        Approve LOA request.
        """
        loa = get_object_or_404(LOA, id=request_id, approved=False)
        loa.approved = True
        loa.save()

        context = {"user": loa.user, "loa": loa}
        Email(
            subject="Your LOA request has been approved!",
            html_body=render_to_string("loa_approved.html", context=context),
            text_body=render_to_string("loa_approved.txt", context=context),
            to_email=loa.user.email,
        ).save()

        return Response(status=status.HTTP_200_OK)

    def delete(self, request, request_id):
        """
        Reject LOA request.
        """
        loa = get_object_or_404(LOA, id=request_id, approved=False)

        context = {"user": loa.user, "reason": request.data.get("reason")}
        Email(
            subject="An update on your LOA request...",
            html_body=render_to_string("loa_rejected.html", context=context),
            text_body=render_to_string("loa_rejected.txt", context=context),
            to_email=loa.user.email,
        ).save()

        loa.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
