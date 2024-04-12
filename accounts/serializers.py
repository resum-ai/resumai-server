from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


from dj_rest_auth.registration.serializers import (
    RegisterSerializer as DefaultRegisterSerializer,
)


class UserRegisterSerializer(DefaultRegisterSerializer):
    username = serializers.CharField(max_length=50, write_only=True, required=True)

    def custom_signup(self, request, user):
        name = self.validated_data.pop("username")
        if name:
            user.username = name
            user.save()


class KakaoTokenSerializer(serializers.Serializer):
    access_token = serializers.CharField()
    code = serializers.CharField()


class UserInfoUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "position", "profile_image")


class GetUserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "position", "profile_image")
