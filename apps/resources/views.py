from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from zhu_core.permissions import IsGet, IsStaff
from .serializers import *


class ResourceListView(APIView):
    permission_classes = [IsGet | IsStaff]

    def get(self, request):
        """
        Get list of all resources.
        """
        resources = Resource.objects.all()
        serializer = ResourceGroupedSerializer(resources)
        return Response(serializer.data)

    def post(self, request):
        """
        Add a new resource.
        """
        serializer = ResourceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResourceInstanceView(APIView):
    permission_classes = [IsStaff]

    def patch(self, request, resource_id):
        """
        Modify resource details.
        """
        resource = get_object_or_404(Resource, id=resource_id)
        serializer = ResourceSerializer(resource, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, resource_id):
        """
        Delete resource.
        """
        resource = get_object_or_404(Resource, id=resource_id)
        resource.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
