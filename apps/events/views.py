from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from zhu_core.permissions import IsStaff, IsMember, ReadOnly
from .models import Event, EventPositionRequest, EventPosition, SupportRequest
from .serializers import EventSerializer, EventWithPositionsSerializer, EventPositionRequestSerializer, \
    EventPositionSerializer


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
        serializer = EventPositionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PositionInstanceView(APIView):
    permission_classes = [IsStaff]

    def put(self, request, position_id, format=None):
        """
        Assign event position.
        """
        event_position = get_object_or_404(EventPosition, id=position_id)
        serializer = EventPositionRequestSerializer(event_position, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, position_id, format=None):
        """
        Delete event position.
        """
        event_position_request = get_object_or_404(EventPosition, position=position_id)
        event_position_request.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RequestPositionView(APIView):
    permission_classes = [IsMember]

    def post(self, request, position_id, format=None):
        """
        Request event position.
        """
        event_position = get_object_or_404(EventPosition, id=position_id)
        serializer = EventPositionRequestSerializer(data={'position': event_position.id}, context={'request': request})
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


class PositionRequestInstanceView(APIView):
    permission_classes = [IsStaff]

    def put(self, request, request_id, format=None):
        """
        Accept event position request.
        Deletes all other requests by user.
        """
        position_request = get_object_or_404(EventPositionRequest, id=request_id)
        position_request.accept_request()
        position_request.user.event_position_requests.filter(position__event=position_request.position.event).delete()

    def delete(self, request, request_id, format=None):
        """
        Reject event position request.
        """
        event_position_request = get_object_or_404(EventPositionRequest, id=request_id)
        event_position_request.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RequestSupportView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        """
        Request support for event.
        """
        serializer = EventPositionRequestSerializer(data=request.data, context={'request': request})
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


# TODO: Return Response() on position request PUT.
# TODO: Return Response() on support request PUT.
# TODO: Send email on position assignment.
# TODO: Send email on support request received/approved/rejected.
