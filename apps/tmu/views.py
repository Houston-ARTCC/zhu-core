from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from zhu_core.permissions import ReadOnly
from .models import METAR
from .serializers import *


class ATISListView(APIView):
    permission_classes = []

    def get(self, request, format=None):
        """
        Get list of all ATIS.
        """
        atis = ATIS.objects.all()
        serializer = ATISSerializer(atis, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        """
        Create new ATIS (from vATIS).
        """
        ATIS.objects.filter(facility=request.data.get('facility')).delete()
        serializer = ATISSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TMUListView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [ReadOnly | IsAuthenticated]

    def get(self, request, format=None):
        """
        Get list of all TMU notices.
        """
        notices = TMUNotice.objects.all()
        serializer = TMUNoticeSerializer(notices, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        """
        Add a new TMU notice.
        """
        serializer = TMUNoticeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TMUInstanceView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request, notice_id, format=None):
        """
        Delete TMU notice.
        """
        resource = get_object_or_404(TMUNotice, id=notice_id)
        resource.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class METARListView(APIView):
    permission_classes = [ReadOnly]

    def get(self, request, format=None):
        """
        Get list of all METARs.
        """
        metars = METAR.objects.all()
        serializer = METARSerializer(metars, many=True)
        return Response(serializer.data)


class METARInstanceView(APIView):
    permission_classes = [ReadOnly]

    def get(self, request, facility, format=None):
        """
        Get METAR for facility.
        """
        metar = get_object_or_404(METAR, facility=facility)
        serializer = METARSerializer(metar)
        return Response(serializer.data)
