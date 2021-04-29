from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from zhu_core.permissions import IsAdmin
from .serlaizers import LOASerializer, BaseLOASerializer
from ..loa.models import LOA


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
        serializer = BaseLOASerializer(data=request.data, context={'request': request})
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

        # TODO: Send email on LOA approval

        return Response(status=status.HTTP_200_OK)

    def delete(self, request, request_id):
        """
        Reject LOA request.
        """
        loa = get_object_or_404(LOA, id=request_id, approved=False)

        # TODO: Send email on LOA rejection

        loa.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
