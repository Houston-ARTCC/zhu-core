from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import ProfileSerializer


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Returns an OAuth profile token for the currently authenticated used.
        """
        serializer = ProfileSerializer(request.user)
        return Response(serializer.data)
