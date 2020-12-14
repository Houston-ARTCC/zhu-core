from rest_framework.response import Response
from rest_framework.views import APIView

from zhu_core.permissions import ReadOnly, IsStaff
from .models import User, Status
from .serializers import UserSerializer, AuthenticatedUserSerializer


class ActiveUserListView(APIView):
    permission_classes = [ReadOnly]

    def get(self, request, format=None):
        """
        Get list of all active users.
        """
        users = User.objects.filter(Status.ACTIVE)
        if request.user.is_authenticated and request.user.is_staff:
            serializer = AuthenticatedUserSerializer(users, many=True)
        else:
            serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


class UserListView(APIView):
    permission_classes = [IsStaff]

    def get(self, request, format=None):
        """
        Get list of all users.
        """
        users = User.objects.all()
        serializer = AuthenticatedUserSerializer(users, many=True)
        return Response(serializer.data)
