from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Event
from .serializers import EventSerializer, EventWithPositionsSerializer


class EventListView(APIView):
    authentication_classes = []

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
    authentication_classes = []

    def get(self, request, id, format=None):
        """
        Get event details.
        """
        event = get_object_or_404(Event, id=id)
        serializer = EventWithPositionsSerializer(event)
        return Response(serializer.data)

    def put(self, request, id, format=None):
        """
        Modify event details.
        """
        event = get_object_or_404(Event, id=id)
        serializer = EventWithPositionsSerializer(event, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id, format=None):
        """
        Delete event.
        """
        event = get_object_or_404(Event, id=id)
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
