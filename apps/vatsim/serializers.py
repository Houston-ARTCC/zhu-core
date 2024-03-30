from django.contrib.auth.models import update_last_login
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import User

from .oauth import process_oauth


class VatsimTokenObtainSerializer(serializers.Serializer):
    code = serializers.CharField()

    def validate(self, attrs):
        authenticate_kwargs = {"code": attrs["code"]}
        try:
            authenticate_kwargs["request"] = self.context["request"]
        except KeyError:
            pass

        user = process_oauth(attrs["code"])
        refresh = RefreshToken.for_user(user)

        data = {
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
        }

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, user)

        return data


class VatsimTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        token = self.token_class(attrs["refresh"])

        # Update rating from VATSIM
        user = User.objects.get(cid=token["user_id"])
        user.update_rating()

        # Add on the updated profile data
        # This way, we can avoid an extra trip to API
        data["profile"] = ProfileSerializer(user).data

        return data


class ProfileSerializer(serializers.ModelSerializer):
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["cid", "first_name", "last_name", "email", "rating", "home_facility", "permissions"]

    def get_permissions(self, user):
        return {
            "is_member": user.is_member,
            "is_training_staff": user.is_training_staff,
            "is_staff": user.is_staff,
            "is_admin": user.is_admin,
        }
