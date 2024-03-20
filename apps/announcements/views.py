import bleach
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from zhu_core.permissions import IsGet, IsStaff

from .models import Announcement
from .serializers import AnnouncementSerializer, BaseAnnouncementSerializer


class AnnouncementListView(APIView):
    permission_classes = [IsGet | IsStaff]

    def get(self, request):
        """
        Get list of all announcements.
        """
        announcements = Announcement.objects.all().order_by("-posted")
        serializer = AnnouncementSerializer(announcements, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Post a new announcement.
        """
        request.data["body"] = bleach.clean(request.data["body"], tags=settings.BLEACH_ALLOWED_TAGS)
        request.data["body"] = request.data["body"].replace("<p><br></p>", "")
        serializer = BaseAnnouncementSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AnnouncementInstanceView(APIView):
    permission_classes = [IsStaff]

    def delete(self, request, announcement_id):
        """
        Delete announcement
        """
        announcement = get_object_or_404(Announcement, id=announcement_id)
        announcement.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecentAnnouncementListView(APIView):
    permission_classes = [IsGet]

    def get(self, request):
        """
        Get list of 4 newest announcements.
        """
        announcements = Announcement.objects.all().order_by("-posted")[:4]
        serializer = AnnouncementSerializer(announcements, many=True)
        return Response(serializer.data)
