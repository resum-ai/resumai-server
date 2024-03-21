import os

import environ
from pathlib import Path
from django.db import transaction
from drf_spectacular.utils import extend_schema, OpenApiResponse

import requests
from django.shortcuts import redirect
from json.decoder import JSONDecodeError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.kakao import views as kakao_view
from .models import CustomUser
from .serializers import UserInfoUpdateSerializer, GetUserInfoSerializer

# 환경변수 세팅
base_dir = Path(__file__).resolve().parent.parent
env_file = base_dir / ".env"

if os.getenv("DJANGO_ENV") == "production":
    env_file = base_dir / ".env.prod"

env = environ.Env()
env.read_env(env_file)

BASE_URL = env("BASE_URL")
KAKAO_CALLBACK_URI = BASE_URL + "accounts/kakao/callback/"
REST_API_KEY = env("KAKAO_REST_API_KEY")
CLIENT_SECRET = env("KAKAO_CLIENT_SECRET_KEY")


@extend_schema(
    summary="카카오 로그인",
    description="카카오 로그인 페이지로 리다이렉트합니다.",
    responses={
        302: OpenApiResponse(
            description="Redirects to the Kakao login page.", response=None
        )
    },
)
@api_view(["GET"])
@permission_classes([AllowAny])
def kakao_login(request):
    return redirect(
        f"https://kauth.kakao.com/oauth/authorize?client_id={REST_API_KEY}&redirect_uri={KAKAO_CALLBACK_URI}&response_type=code"
    )


@extend_schema(exclude=True)
@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def kakao_callback(request):
    code = request.GET.get("code")

    # Access Token Request
    token_req = requests.get(
        f"https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={REST_API_KEY}&client_secret={CLIENT_SECRET}&redirect_uri={KAKAO_CALLBACK_URI}&code={code}"
    )

    token_req_json = token_req.json()

    error = token_req_json.get("error")
    if error is not None:
        raise JSONDecodeError(error)

    access_token = token_req_json.get("access_token")

    # Email Request

    profile_request = requests.get(
        "https://kapi.kakao.com/v2/user/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    profile_data = profile_request.json()

    kakao_oid = profile_data.get("id")
    kakao_account = profile_data.get("kakao_account")
    username = kakao_account["profile"]["nickname"]
    profile_image_url = kakao_account["profile"]["profile_image_url"]
    email = kakao_account.get("email")

    # 회원가입, 로그인 로직

    data = {"access_token": access_token, "code": code}

    try:
        user = CustomUser.objects.get(email=email)
        # 유저가 존재하는 경우
        accept = requests.post(f"{BASE_URL}accounts/kakao/login/finish/", data=data)
        accept_status = accept.status_code

        if accept_status != 200:
            return Response({"err_msg": "failed to signin"}, status=accept_status)

        accept_json = accept.json()
        # key 이름 변경
        accept_json['accessToken'] = accept_json.pop('access')
        accept_json['refreshToken'] = accept_json.pop('refresh')
        accept_json['userProfile'] = accept_json.pop('user')
        accept_json['userProfile']['id'] = accept_json['userProfile'].pop('pk')
        return Response(accept_json)

    except CustomUser.DoesNotExist:
        # 기존에 가입된 유저가 없으면 새로 가입
        accept = requests.post(f"{BASE_URL}accounts/kakao/login/finish/", data=data)
        accept_status = accept.status_code
        if accept_status != 200:
            return Response({"err_msg": "failed to signup"}, status=accept_status)

        # user의 pk, email, first name, last name과 Access Token, Refresh token 가져옴
        accept_json = accept.json()
        # key 이름 변경
        accept_json['accessToken'] = accept_json.pop('access')
        accept_json['refreshToken'] = accept_json.pop('refresh')
        accept_json['userProfile'] = accept_json.pop('user')
        accept_json['userProfile']['id'] = accept_json['userProfile'].pop('pk')
        return Response(accept_json)


class KakaoLoginView(SocialLoginView):
    adapter_class = kakao_view.KakaoOAuth2Adapter
    client_class = OAuth2Client
    callback_url = KAKAO_CALLBACK_URI


class UpdateUserInfoView(APIView):
    permission_classes = [IsAuthenticated]  # 인증된 사용자만 접근 가능하도록 설정

    @extend_schema(
        summary="유저 정보 업데이트",
        request=UserInfoUpdateSerializer,
        responses={200: UserInfoUpdateSerializer},
    )
    def put(self, request, *args, **kwargs):
        print(request.user)
        user = request.user

        # 유저 데이터 가져옴
        new_username = request.data.get("username")
        new_profile_image = request.data.get("profile_image")
        new_position = request.data.get("position")

        # 유저 데이터 비교
        user.username = new_username if new_username is not None else user.username
        user.profile_image = (
            new_profile_image if new_profile_image is not None else user.profile_image
        )
        user.position = new_position if new_position is not None else user.position
        user.save()

        # 업데이트된 사용자 정보를 반환
        serializer = UserInfoUpdateSerializer(user)
        return Response(serializer.data)


class GetUserInfoView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="유저 정보 반환",
        request=GetUserInfoSerializer,
        responses={200: GetUserInfoSerializer},
    )
    def get(self, request):
        user = request.user

        serializer = GetUserInfoSerializer(user)
        print(serializer.data)

        return Response(serializer.data)
