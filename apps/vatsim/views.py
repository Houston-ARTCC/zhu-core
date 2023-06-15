from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenViewBase

from .serializers import *


class MyTokenObtainPairView(TokenViewBase):
    """
    Takes a VATSIM OAuth2 authentication code and returns an access and refresh
    JSON web token pair to prove the authentication of the VATSIM user.
    """
    serializer_class = MyTokenObtainPairSerializer


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Returns an OAuth profile token for the currently authenticated used.
        """
        return Response({
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'cid': request.user.cid,
            'email': request.user.email,
            'rating': request.user.rating,
            'facility': request.user.home_facility,
            'is_member': request.user.is_member,
            'is_training_staff': request.user.is_training_staff,
            'is_staff': request.user.is_staff,
            'is_senior_staff': request.user.is_senior_staff,
            'is_admin': request.user.is_admin,
        })
