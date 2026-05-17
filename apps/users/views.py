import os
from collections import defaultdict
from io import BytesIO

import requests
from django.core.files import File
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string
from PIL import Image
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.feedback.models import Feedback
from apps.feedback.serializers import BasicFeedbackSerializer
from zhu_core.permissions import IsAdmin, IsController, IsDelete, IsGet, IsPatch, IsPut, IsStaff, IsTrainingStaff
from zhu_core.settings import MEDIA_ROOT

from .models import Status, User
from .serializers import (
    AdminEditUserSerializer,
    AuthenticatedUserSerializer,
    BasicUserSerializer,
    EndorsementOnlyEditSerializer,
    UserSerializer,
)


class ActiveUserListView(APIView):
    def get(self, request):
        """
        Get list of all active users sorted by first name.
        Sorted into home and visiting controllers.
        """
        users = User.objects.filter(status=Status.ACTIVE).prefetch_related("roles").order_by("first_name")
        if request.user.is_authenticated and request.user.is_staff:
            serializer_class = AuthenticatedUserSerializer
        else:
            serializer_class = UserSerializer
        return Response(
            {
                "home": serializer_class(users.filter(roles__short="HC"), many=True).data,
                "visiting": serializer_class(users.filter(roles__short="VC"), many=True).data,
            }
        )


class UserInstanceView(APIView):
    permission_classes = [
        (IsDelete & IsAdmin)
        | (IsPut & IsController)
        | (IsPatch & (IsStaff | IsTrainingStaff))
        | (IsGet | IsStaff)
    ]

    def get(self, request, cid):
        """
        Get user details.
        """
        user = get_object_or_404(User, ~Q(status=Status.NON_MEMBER), cid=cid)

        if request.user.is_authenticated and request.user.is_staff:
            serializer = AuthenticatedUserSerializer(user)
        else:
            serializer = UserSerializer(user)

        return Response(serializer.data)

    def put(self, request, cid):
        """
        Allows for the user to update their profile photo or biography.
        """
        user = get_object_or_404(User, cid=cid)

        if "avatar" in request.data:
            if user.profile:
                os.remove(os.path.join(MEDIA_ROOT, user.profile.name))
                user.profile = None

            if request.data.get("avatar"):
                img = Image.open(request.data.get("avatar"))
                img = img.resize((500, 500), Image.LANCZOS)

                profile_io = BytesIO()
                img.save(profile_io, "PNG")

                user.profile = File(profile_io, name=f"{get_random_string(8)}.png")

        if "biography" in request.data:
            user.biography = request.data.get("biography")

        user.save()

        return Response(UserSerializer(user).data)

    def patch(self, request, cid):
        """
        Modify user details.

        - Training admins (TA/ATA) and admins get the full AdminEditUserSerializer.
        - Instructors get endorsement-only edits (any endorsement).
        - Mentors get endorsement-only edits, restricted to endorsements they hold.
        - Anyone else (e.g. self-edit by non-staff) falls back to AuthenticatedUserSerializer.
        """
        user = get_object_or_404(User, cid=cid)
        requester = request.user

        if requester.is_training_admin:
            serializer = AdminEditUserSerializer(user, data=request.data, partial=True)
        elif requester.is_staff:
            serializer = AuthenticatedUserSerializer(user, data=request.data, partial=True)
        elif requester.is_training_staff:
            # MTR (without INS) is restricted to endorsements they themselves hold.
            is_mentor_only = (
                requester.roles.filter(short="MTR").exists()
                and not requester.roles.filter(short="INS").exists()
            )
            allowed_keys = None
            if is_mentor_only:
                allowed_keys = {
                    key for key, value in (requester.endorsements or {}).items() if value
                }
            serializer = EndorsementOnlyEditSerializer(
                user, data=request.data, partial=True, allowed_keys=allowed_keys
            )
        else:
            serializer = AuthenticatedUserSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, cid):
        """
        Remove user from roster.
        Automatically removes user from VATUSA roster.
        """
        user = get_object_or_404(User, cid=cid)

        if user.membership == "HC":
            requests.delete(
                f"https://api.vatusa.net/v2/facility/ZHU/roster/{user.cid}",
                data={"reason": request.data.get("reason"), "by": request.user.cid},
                params={"apikey": os.getenv("VATUSA_API_TOKEN")},
            )
        elif user.membership == "VC":
            requests.delete(
                f"https://api.vatusa.net/v2/facility/ZHU/roster/manageVisitor/{cid}",
                data={"reason": request.data.get("reason")},
                params={"apikey": os.getenv("VATUSA_API_TOKEN")},
            )

        user.set_membership(None)
        return Response(status.HTTP_204_NO_CONTENT)


class UserFeedbackView(APIView):
    permission_classes = [IsController | IsStaff | IsTrainingStaff]

    def get(self, request, cid):
        """
        Get list of all approved feedback for user.
        """
        feedback = Feedback.objects.filter(controller__cid=cid).filter(approved=True)
        serializer = BasicFeedbackSerializer(feedback, many=True)
        return Response(serializer.data)


class SimplifiedActiveUserListView(APIView):
    def get(self, request):
        """
        Get list of all active users sorted by first name.
        Only includes basic information (CID, name, initials, profile).
        Sorted into home and visiting controllers.
        """
        users = User.objects.filter(status=Status.ACTIVE).order_by("first_name")
        return Response(
            {
                "home": BasicUserSerializer(users.filter(roles__short="HC"), many=True).data,
                "visiting": BasicUserSerializer(users.filter(roles__short="VC"), many=True).data,
            }
        )


class NewestUserListView(APIView):
    def get(self, request):
        """
        Get list of 3 newest controllers.
        """
        users = User.objects.exclude(status=Status.NON_MEMBER).order_by("-joined")[:3]
        serializer = BasicUserSerializer(users, many=True)
        return Response(serializer.data)


class StaffListView(APIView):
    permission_classes = [IsGet]

    def get(self, request):
        """
        Get list of ARTCC staff.
        """
        shorts = ["ATM", "DATM", "TA", "ATA", "FE", "AFE", "EC", "AEC", "WM", "AWM", "INS", "MTR", "WEB"]
        users = User.objects.filter(roles__short__in=shorts).prefetch_related("roles").distinct()

        by_role = defaultdict(list)
        for user in users:
            for role in user.roles.all():
                if role.short in shorts:
                    by_role[role.short].append(user)

        def head(short):
            return BasicUserSerializer(by_role[short][0]).data if by_role[short] else None

        def many(short):
            return BasicUserSerializer(by_role[short], many=True).data

        return Response(
            {
                "atm": {"user": head("ATM")},
                "datm": {"user": head("DATM")},
                "ta": {"user": head("TA"), "assistants": many("ATA")},
                "fe": {"user": head("FE"), "assistants": many("AFE")},
                "ec": {"user": head("EC"), "assistants": many("AEC")},
                "wm": {"user": head("WM"), "assistants": many("AWM")},
                "ins": many("INS"),
                "mtr": many("MTR"),
                "web": many("WEB"),
            }
        )
