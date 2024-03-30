from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.loa.models import LOA
from apps.mailer.models import Email
from zhu_core.permissions import IsAdmin, IsMember

from .serializers import BaseLOASerializer, LOASerializer


class LOAListView(APIView):
    permission_classes = [IsMember]

    def get(self, request):
        """
        Get list of one's LOAs, both approved and unapproved, that end in the future.
        """
        loas = request.user.loas.filter(end__gte=timezone.now())
        serializer = LOASerializer(loas, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Submit an LOA request.
        """
        serializer = BaseLOASerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LOAInstanceView(APIView):
    permission_classes = [IsMember]

    def delete(self, request, loa_id):
        """
        Cancel leave of absence.
        """
        loa = get_object_or_404(LOA, id=loa_id, user=request.user)
        loa.delete()

        request.user.update_loa_status()

        return Response(status=status.HTTP_204_NO_CONTENT)


class LOAAdminListView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        """
        Get list of all LOAs, both approved and unapproved, that end in the future.
        """
        loas = LOA.objects.filter(end__gte=timezone.now())
        serializer = LOASerializer(loas, many=True)
        return Response(serializer.data)


class LOAAdminInstanceView(APIView):
    permission_classes = [IsAdmin]

    def put(self, request, loa_id):
        """
        Approve LOA request.
        """
        loa = get_object_or_404(LOA, id=loa_id, approved=False)
        loa.approved = True
        loa.save()

        Email.objects.queue(
            to=loa.user,
            subject="Your LOA has been approved",
            from_email="management@houston.center",
            template="loa_approved",
            context={"loa": loa},
        )

        return Response(status=status.HTTP_200_OK)

    def delete(self, request, loa_id):
        """
        Reject LOA request.
        """
        loa = get_object_or_404(LOA, id=loa_id, approved=False)

        Email.objects.queue(
            to=loa.user,
            subject="An update on your LOA request",
            from_email="management@houston.center",
            template="loa_rejected",
            context={"reason": request.data.get("reason")},
        )

        loa.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
