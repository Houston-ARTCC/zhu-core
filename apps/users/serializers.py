from rest_framework import serializers

from .models import User, Role


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    rating = serializers.SerializerMethodField(read_only=True)
    roles = RoleSerializer(many=True, read_only=True)

    class Meta:
        model = User
        exclude = ['email', 'password', 'groups', 'user_permissions']

    def get_rating(self, obj):
        return {
            'short': obj.rating,
            'long': obj.get_rating_display()
        }


class AuthenticatedUserSerializer(serializers.ModelSerializer):
    rating = serializers.SerializerMethodField(read_only=True)
    roles = RoleSerializer(many=True)
    profile = serializers.ImageField(read_only=True)

    class Meta:
        model = User
        exclude = ['password']

    def get_rating(self, obj):
        return {
            'short': obj.rating,
            'long': obj.get_rating_display()
        }

    def update(self, instance, validated_data):
        roles = validated_data.pop('roles', [])
        instance = super().update(instance, validated_data)
        instance.roles.set([Role.objects.filter(short=role.get('short')).first() for role in roles])
        return instance


class BaseUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['cid', 'first_name', 'last_name', 'initials', 'profile']


class AuthenticatedBaseUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['cid', 'first_name', 'last_name', 'initials', 'profile', 'email']
