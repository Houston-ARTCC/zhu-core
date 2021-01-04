from rest_framework import serializers

from .models import User, Role


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['short', 'long']


class UserSerializer(serializers.ModelSerializer):
    rating = serializers.SerializerMethodField(read_only=True)
    roles = RoleSerializer(many=True, read_only=True)

    class Meta:
        model = User
        exclude = ['email', 'password']

    def get_rating(self, obj):
        return {
            'short': obj.rating,
            'long': obj.get_rating_display()
        }


class AuthenticatedUserSerializer(serializers.ModelSerializer):
    rating = serializers.SerializerMethodField(read_only=True)
    roles = RoleSerializer(many=True, read_only=True)

    class Meta:
        model = User
        exclude = ['password']

    def get_rating(self, obj):
        return {
            'short': obj.rating,
            'long': obj.get_rating_display()
        }


class BasicUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['cid', 'first_name', 'last_name', 'initials', 'profile']
