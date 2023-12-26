import os

from discord_webhook import DiscordEmbed, DiscordWebhook
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import User
from zhu_core.permissions import IsGet, IsMember, IsStaff

from .models import Event, EventPosition, EventScore, PositionShift, ShiftRequest, SupportRequest
from .serializers import (
    BasePositionSerializer,
    BaseShiftRequestSerializer,
    BaseShiftSerializer,
    BaseSupportRequestSerializer,
    BasicEventSerializer,
    EventScoreSerializer,
    EventSerializer,
    PositionPreset,
    PositionPresetSerializer,
    SupportRequestSerializer,
)


class EventsListView(APIView):
    permission_classes = [IsGet | IsStaff]

    def get(self, request):
        """
        Get list of all events.
        """
        events = Event.objects.filter(end__gt=timezone.now()).order_by("start")

        if not (request.user.is_authenticated and request.user.is_staff):
            events = events.exclude(hidden=True)

        serializer = BasicEventSerializer(events, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Add a new event.
        """
        serializer = EventSerializer(data=request.data)
        if serializer.is_valid():
            event = serializer.save()

            if "preset" in request.data:
                preset_filter = PositionPreset.objects.filter(id=request.data.get("preset"))
                if preset_filter.exists():
                    preset_filter.first().apply_to_event(event)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ArchivedEventsListView(APIView):
    permission_classes = [IsGet]

    def get(self, request):
        """
        Get list of all archived events.
        """
        events = Event.objects.filter(end__lt=timezone.now()).order_by("-start")

        if not (request.user.is_authenticated and request.user.is_staff):
            events = events.exclude(hidden=True)

        serializer = BasicEventSerializer(events, many=True)
        return Response(serializer.data)


class EventInstanceView(APIView):
    permission_classes = [IsGet | IsStaff]

    def get(self, request, event_id):
        """
        Get event details.
        """
        event = get_object_or_404(Event, id=event_id)

        if event.hidden and not request.user.is_staff:
            raise PermissionDenied("You do not have permission to view this event.")

        serializer = EventSerializer(event)
        return Response(serializer.data)

    def patch(self, request, event_id):
        """
        Modify event details.
        """
        event = get_object_or_404(Event, id=event_id)
        serializer = EventSerializer(event, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, event_id):
        """
        Post positions to designated events Discord channel.
        """
        event = get_object_or_404(Event, id=event_id)
        url = f"https://www.zhuartcc.org/events/{event.id}"
        webhook = DiscordWebhook(url=os.getenv("EVENTS_WEBHOOK_URL"))
        embed = DiscordEmbed(
            title=f':calendar: "{event.name}"',
            description=f"Below are the tentative event position assignments as they currently stand. Assignments are"
            f"subject to change on the day of the event so you should always double check the event page"
            f"before logging on to control.\n**[View the event page here!]({url})**",
            color="109cf1",
        )
        for position in event.positions.all():
            embed.add_embed_field(
                name=position.callsign,
                value="\n".join(
                    [
                        f"`{i + 1}` *{shift.user.full_name}*" if shift.user is not None else f"`{i + 1}`"
                        for i, shift in enumerate(position.shifts.all())
                    ]
                ),
            )
        embed.set_image(url=event.banner)
        webhook.add_embed(embed)
        res = webhook.execute()

        return Response(res.content, status=res.status_code)

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
        serializer = BasePositionSerializer(
            data={
                "event": event.id,
                "callsign": request.data.get("callsign"),
            }
        )
        if serializer.is_valid():
            serializer.save()

            for _ in range(int(request.data.get("shifts"))):
                PositionShift(position=serializer.instance).save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PositionInstanceView(APIView):
    permission_classes = [IsStaff]

    def post(self, request, position_id):
        """
        Add event shift.
        """
        position = get_object_or_404(EventPosition, id=position_id)
        serializer = BaseShiftSerializer(
            data={
                "position": position.id,
                "start": request.data.get("start"),
                "end": request.data.get("end"),
            }
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, position_id):
        """
        Add additional shift to position.
        """
        position = get_object_or_404(EventPosition, id=position_id)
        PositionShift(position=position).save()
        return Response(status=status.HTTP_200_OK)

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

        if shift.position.event.hidden and not request.user.is_staff or request.user.prevent_event_signup:
            raise PermissionDenied("You do not have permission to interact with this event.")

        serializer = BaseShiftRequestSerializer(data={"shift": shift.id}, context={"request": request})
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
            raise PermissionDenied("You do not have permission to interact with this event.")

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
        shift = get_object_or_404(PositionShift, id=shift_id)
        shift.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SupportRequestListView(APIView):
    permission_classes = [(IsGet & IsStaff) | (~IsGet & IsAuthenticated)]

    def get(self, request):
        """
        Get list of all pending event support requests.
        """
        requests = SupportRequest.objects.all()
        serializer = SupportRequestSerializer(requests, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Request support for event.
        """
        serializer = BaseSupportRequestSerializer(data=request.data, context={"request": request})
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


class PositionPresetListView(APIView):
    permission_classes = [IsStaff]

    def get(self, request):
        """
        Get list of all position presets.
        """
        presets = PositionPreset.objects.all()
        serializer = PositionPresetSerializer(presets, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Create new position preset.
        """
        serializer = PositionPresetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PositionPresetInstanceView(APIView):
    permission_classes = [IsStaff]

    def put(self, request, preset_id):
        """
        Modify position preset.
        """
        preset = get_object_or_404(PositionPreset, id=preset_id)
        serializer = PositionPresetSerializer(preset, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, preset_id):
        """
        Remove position preset.
        """
        preset = get_object_or_404(PositionPreset, id=preset_id)
        preset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class EventScoreListView(APIView):
    permission_classes = [IsMember]

    def get(self, request, cid=None):
        """
        Get event scores for user.
        Defaults to session user if cid is not defined.
        """
        if not cid:
            user = request.user
        elif request.user.is_staff:
            # Need to be staff to view another user's scores.
            user = get_object_or_404(User, cid=cid)
        else:
            raise PermissionDenied("You do not have permission to view scores for this user.")

        scores = EventScore.objects.filter(user=user)
        serializer = EventScoreSerializer(scores, many=True)
        return Response(serializer.data)


# TODO: Send email on support request received/approved/rejected.
