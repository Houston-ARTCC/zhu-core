from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from zhu_core.permissions import IsStaff, IsMember, ReadOnly
from .serializers import *


class EventListView(APIView):
    permission_classes = [ReadOnly | IsStaff]

    def get(self, request):
        """
        Get list of all events.
        """
        events = Event.objects.all().order_by('start')

        if not (request.user.is_authenticated and request.user.is_staff):
            events = events.exclude(hidden=True)

        serializer = EventSerializer(events, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Add a new event.
        """
        serializer = EventSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EventInstanceView(APIView):
    permission_classes = [ReadOnly | IsStaff]

    def get(self, request, event_id):
        """
        Get event details.
        """
        event = get_object_or_404(Event, id=event_id)

        if event.hidden and not request.user.is_staff:
            raise PermissionDenied('You do not have permission to view this event.')

        serializer = EventSerializer(event)
        return Response(serializer.data)

    def put(self, request, event_id):
        """
        Modify event details.
        """
        event = get_object_or_404(Event, id=event_id)
        serializer = EventSerializer(event, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, event_id):
        """
        Delete event.
        """
        event = get_object_or_404(Event, id=event_id)
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def post(self, request, event_id):
        """
        Add event position.
        """
        event = get_object_or_404(Event, id=event_id)
        serializer = BasePositionSerializer(data={
            'event': event.id,
            'callsign': request.POST.get('callsign'),
        })
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PositionInstanceView(APIView):
    permission_classes = [IsStaff]

    def post(self, request, position_id):
        """
        Add event shift.
        """
        position = get_object_or_404(EventPosition, id=position_id)
        serializer = BaseShiftSerializer(data={
            'position': position.id,
            'start': request.POST.get('start'),
            'end': request.POST.get('end'),
        })
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, position_id):
        """
        Delete event position.
        """
        event_position = get_object_or_404(EventPosition, id=position_id)
        event_position.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShiftRequestView(APIView):
    permission_classes = [IsMember]

    def post(self, request, shift_id):
        """
        Request event shift.
        """
        shift = get_object_or_404(PositionShift, id=shift_id)

        if shift.position.event.hidden and not request.user.is_staff:
            raise PermissionDenied('You do not have permission to interact with this event.')

        serializer = BaseShiftRequestSerializer(data={'shift': shift.id}, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, shift_id):
        """
        Unrequest event shift.
        """
        shift_request = get_object_or_404(ShiftRequest, shift=shift_id, user=request.user)

        if shift_request.shift.position.event.hidden and not request.user.is_staff:
            raise PermissionDenied('You do not have permission to interact with this event.')

        shift_request.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShiftInstanceView(APIView):
    permission_classes = [IsStaff]

    def patch(self, request, shift_id):
        """
        Assign shift.
        """
        shift = get_object_or_404(PositionShift, id=shift_id)
        serializer = BaseShiftSerializer(shift, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, shift_id):
        """
        Delete shift.
        """
        event_position = get_object_or_404(PositionShift, id=shift_id)
        event_position.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SupportRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Request support for event.
        """
        serializer = SupportRequestSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SupportRequestInstanceView(APIView):
    permission_classes = [IsStaff]

    def put(self, request, request_id):
        """
        Approve support request.
        """
        support_request = get_object_or_404(SupportRequest, id=request_id)
        support_request.convert_to_event()
        support_request.delete()
        return Response(status=status.HTTP_201_CREATED)

    def delete(self, request, request_id):
        """
        Reject support request.
        """
        event_position_request = get_object_or_404(SupportRequest, id=request_id)
        event_position_request.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# TODO: Send email on position assignment.
# TODO: Send email on support request received/approved/rejected.
