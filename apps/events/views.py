from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from zhu_core.permissions import IsStaff, IsMember, ReadOnly
from .serializers import *


class EventListView(APIView):
    permission_classes = [ReadOnly | IsStaff]

    def get(self, request, format=None):
        """
        Get list of all events.
        """
        events = Event.objects.all()
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
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

    def get(self, request, event_id, format=None):
        """
        Get event details.
        """
        event = get_object_or_404(Event, id=event_id)
        serializer = EventWithPositionsSerializer(event)
        return Response(serializer.data)

    def put(self, request, event_id, format=None):
        """
        Modify event details.
        """
        event = get_object_or_404(Event, id=event_id)
        serializer = EventWithPositionsSerializer(event, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, event_id, format=None):
        """
        Delete event.
        """
        event = get_object_or_404(Event, id=event_id)
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def post(self, request, event_id, format=None):
        """
        Add event position.
        """
        event = get_object_or_404(Event, id=event_id)
        request.data['event'] = event.id
        serializer = PositionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PositionInstanceView(APIView):
    permission_classes = [IsStaff]

    def patch(self, request, position_id, format=None):
        """
        Assign event position.
        Deletes all other requests by user.
        """
        event_position = get_object_or_404(EventPosition, id=position_id)
        serializer = BasePositionSerializer(event_position, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            if event_position.user is not None:
                event_position.user.event_position_requests.filter(position__event=event_position.event).delete()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, position_id, format=None):
        """
        Delete event position.
        """
        event_position = get_object_or_404(EventPosition, id=position_id)
        event_position.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RequestPositionView(APIView):
    permission_classes = [IsMember]

    def post(self, request, position_id, format=None):
        """
        Request event position.
        """
        event_position = get_object_or_404(EventPosition, id=position_id)
        serializer = BasePositionRequestSerializer(data={'position': event_position.id}, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, position_id, format=None):
        """
        Unrequest event position.
        """
        event_position_request = get_object_or_404(EventPositionRequest, position=position_id, user=request.user)
        event_position_request.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RequestSupportView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        """
        Request support for event.
        """
        serializer = PositionRequestSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SupportRequestInstanceView(APIView):
    permission_classes = [IsStaff]

    def put(self, request, request_id, format=None):
        """
        Approve support request.
        """
        event_position = get_object_or_404(SupportRequest, id=request_id)
        event_position.convert_to_event()
        event_position.delete()

    def delete(self, request, request_id, format=None):
        """
        Reject support request.
        """
        event_position_request = get_object_or_404(SupportRequest, position=request_id)
        event_position_request.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# TODO: Clean up views by using generic views.
# TODO: Return Response() on support request PUT.
# TODO: Send email on position assignment.
# TODO: Send email on support request received/approved/rejected.
