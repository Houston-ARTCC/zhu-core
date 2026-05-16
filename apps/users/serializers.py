from rest_framework import serializers

from zhu_core.utils import StrictReadOnlyFieldsMixin

from .models import Role, User


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["short", "long"]


class UserSerializer(serializers.ModelSerializer):
    rating = serializers.SerializerMethodField(read_only=True)
    roles = RoleSerializer(many=True, read_only=True)

    class Meta:
        model = User
        exclude = [
            "email",
            "password",
            "groups",
            "user_permissions",
            "is_superuser",
            "last_login",
            "prevent_event_signup",
        ]

    def get_rating(self, obj):
        return {"short": obj.rating, "long": obj.get_rating_display()}


class AuthenticatedUserSerializer(StrictReadOnlyFieldsMixin, serializers.ModelSerializer):
    rating = serializers.SerializerMethodField(read_only=True)
    roles = RoleSerializer(many=True, read_only=True)
    profile = serializers.ImageField(read_only=True)

    class Meta:
        model = User
        exclude = ["password", "groups", "user_permissions", "is_superuser"]

    def get_rating(self, obj):
        return {"short": obj.rating, "long": obj.get_rating_display()}


class AdminEditUserSerializer(AuthenticatedUserSerializer):
    roles = RoleSerializer(many=True)

    def update(self, instance, validated_data):
        roles = validated_data.pop("roles", [])
        instance = super().update(instance, validated_data)
        instance.roles.set([Role.objects.filter(short=role.get("short")).first() for role in roles])
        return instance


class EndorsementOnlyEditSerializer(serializers.ModelSerializer):
    """
    Lets training staff edit endorsements without touching anything else.
    Mentors are restricted to flipping endorsements they themselves hold;
    Instructors can flip any endorsement.
    """

    class Meta:
        model = User
        fields = ["endorsements"]

    def __init__(self, *args, allowed_keys=None, **kwargs):
        self._allowed_keys = allowed_keys
        super().__init__(*args, **kwargs)

    def validate_endorsements(self, value):
        if self._allowed_keys is None:
            return value
        bad = [key for key in value if key not in self._allowed_keys]
        if bad:
            raise serializers.ValidationError(
                f"Not authorized to modify these endorsements: {', '.join(bad)}"
            )
        return value

    def update(self, instance, validated_data):
        # Merge into existing dict so partial updates don't blow away keys.
        new = validated_data.get("endorsements", {})
        merged = {**(instance.endorsements or {}), **new}
        instance.endorsements = merged
        instance.save()
        return instance


class BasicUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["cid", "first_name", "last_name", "initials", "profile"]


class AuthenticatedBasicUserSerializer(BasicUserSerializer):
    class Meta:
        model = User
        fields = [*BasicUserSerializer.Meta.fields, "email"]
