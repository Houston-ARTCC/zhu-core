from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from zhu_core.permissions import IsStaff, IsMember, ReadOnly
from .models import Event, EventPositionRequest, EventPosition
from .serializers import EventSerializer, EventWithPositionsSerializer, EventPositionRequestSerializer


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


class RequestPositionView(APIView):
    permission_classes = [IsMember]

    def post(self, request, event_id, position_id, format=None):
        """
        Request event position.
        """
        event_position = get_object_or_404(EventPosition, id=position_id)
        serializer = EventPositionRequestSerializer(data={'position': event_position.id}, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, event_id, position_id, format=None):
        """
        Unrequest event position.
        """
        event_position_request = get_object_or_404(EventPositionRequest, position=position_id, user=request.user)
        event_position_request.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
