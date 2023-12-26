from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from zhu_core.permissions import IsMember, IsOwner

from .models import Booking
from .serializers import BaseBookingSerializer, BookingSerializer


class BookingListView(APIView):
    permission_classes = [IsMember]

    def get(self, request):
        """
        Get list of own controller bookings.
        """
        bookings = Booking.objects.filter(user=request.user, end__gt=timezone.now())
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Create controller booking.
        """
        serializer = BaseBookingSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BookingInstanceView(APIView):
    permission_classes = [IsOwner]

    def get_object(self, booking_id):
        obj = get_object_or_404(Booking, id=booking_id)
        self.check_object_permissions(self.request, obj)
        return obj

    def delete(self, request, booking_id):
        """
        Cancel controller booking.
        """
        booking = self.get_object(booking_id)
        booking.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
