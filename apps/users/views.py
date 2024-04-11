import base64
import os
from io import BytesIO

import requests
from django.core.files import File
from django.db.models import Q
from django.shortcuts import get_object_or_404
from PIL import Image
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.feedback.models import Feedback
from apps.feedback.serializers import BasicFeedbackSerializer
from zhu_core.permissions import IsAdmin, IsController, IsDelete, IsGet, IsPut, IsStaff, IsTrainingStaff
from zhu_core.settings import BASE_DIR

from .models import Status, User
from .serializers import AdminEditUserSerializer, AuthenticatedUserSerializer, BasicUserSerializer, UserSerializer


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
    permission_classes = [(IsDelete & IsAdmin) | (IsPut & IsController) | (IsGet | IsStaff)]

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
            if request.data.get("avatar"):
                img_data = base64.b64decode(request.data.get("avatar"))
                img = Image.open(BytesIO(img_data))
                img = img.resize((500, 500), Image.ANTIALIAS)

                profile_io = BytesIO()
                img.save(profile_io, "PNG")

                user.profile = File(profile_io, name=f"{user.cid}.png")
            else:
                os.remove(BASE_DIR / f"media/profile/{user.cid}.png")
                user.profile = None
        if "biography" in request.data:
            user.biography = request.data.get("biography")

        user.save()

        return Response(UserSerializer(user).data)

    def patch(self, request, cid):
        """
        Modify user details.
        """
        user = get_object_or_404(User, cid=cid)

        if request.user.is_admin:
            serializer_class = AdminEditUserSerializer
        else:
            serializer_class = AuthenticatedUserSerializer

        serializer = serializer_class(user, data=request.data, partial=True)
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
        atm = BasicUserSerializer(User.objects.filter(roles__short="ATM").first()).data
        datm = BasicUserSerializer(User.objects.filter(roles__short="DATM").first()).data
        ta = BasicUserSerializer(User.objects.filter(roles__short="TA").first()).data
        fe = BasicUserSerializer(User.objects.filter(roles__short="FE").first()).data
        ec = BasicUserSerializer(User.objects.filter(roles__short="EC").first()).data
        wm = BasicUserSerializer(User.objects.filter(roles__short="WM").first()).data
        return Response(
            {
                "atm": {
                    "user": atm if atm.get("cid") else None,
                },
                "datm": {
                    "user": datm if datm.get("cid") else None,
                },
                "ta": {
                    "user": ta if ta.get("cid") else None,
                    "assistants": BasicUserSerializer(User.objects.filter(roles__short="ATA"), many=True).data,
                },
                "fe": {
                    "user": fe if fe.get("cid") else None,
                    "assistants": BasicUserSerializer(User.objects.filter(roles__short="AFE"), many=True).data,
                },
                "ec": {
                    "user": ec if ec.get("cid") else None,
                    "assistants": BasicUserSerializer(User.objects.filter(roles__short="AEC"), many=True).data,
                },
                "wm": {
                    "user": wm if wm.get("cid") else None,
                    "assistants": BasicUserSerializer(User.objects.filter(roles__short="AWM"), many=True).data,
                },
                "ins": BasicUserSerializer(User.objects.filter(roles__short="INS"), many=True).data,
                "mtr": BasicUserSerializer(User.objects.filter(roles__short="MTR"), many=True).data,
                "web": BasicUserSerializer(User.objects.filter(roles__short="WEB"), many=True).data,
            }
        )
