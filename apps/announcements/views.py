import bleach
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from zhu_core.permissions import ReadOnly, IsStaff
from .serializers import *


class AnnouncementListView(APIView):
    permission_classes = [ReadOnly | IsStaff]

    def get(self, request):
        """
        Get list of all announcements.
        """
        announcements = Announcement.objects.all().order_by('-posted')
        serializer = AnnouncementSerializer(announcements, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Post a new announcement.
        """
        request.data['body'] = bleach.clean(request.data['body'], tags=settings.BLEACH_ALLOWED_TAGS)
        serializer = BaseAnnouncementSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
