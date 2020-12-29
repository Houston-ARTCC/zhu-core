from rest_framework_simplejwt.views import TokenViewBase

from .serializers import MyTokenObtainPairSerializer


class MyTokenObtainPairView(TokenViewBase):
    """
    Takes a VATSIM OAuth2 authentication code and returns an access and refresh
    JSON web token pair to prove the authentication of the VATSIM user.
    """
    serializer_class = MyTokenObtainPairSerializer
