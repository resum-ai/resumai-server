from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


from dj_rest_auth.registration.serializers import (
    RegisterSerializer as DefaultRegisterSerializer,
)


class UserRegisterSerializer(DefaultRegisterSerializer):
    name = serializers.CharField(max_length=50, write_only=True, required=True)

    def custom_signup(self, request, user):
        name = self.validated_data.pop("name")
        if name:
            user.username = name
            user.save()


class UserLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class UserInfoUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username", "position", "direct_number", "profile_image", "status")


class GetUserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "position", "direct_number", "profile_image", "status")

