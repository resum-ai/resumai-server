import os

import environ
from pathlib import Path
from django.db import transaction
from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiExample,
    OpenApiParameter,
)
from django.http import JsonResponse

import requests
from django.shortcuts import redirect
from json.decoder import JSONDecodeError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.kakao import views as kakao_view
from .models import CustomUser
from .serializers import (
    UserInfoUpdateSerializer,
    GetUserInfoSerializer,
    KakaoTokenSerializer,
)
import logging

logger = logging.getLogger(__name__)

# 환경변수 세팅
BASE_DIR = Path(__file__).resolve().parent.parent
env_file = BASE_DIR / ".env"
if os.getenv("DJANGO_ENV") == "production":
    env_file = BASE_DIR / ".env.prod"
env = environ.Env()
env.read_env(env_file)

BASE_URL = env("BASE_URL")
KAKAO_CALLBACK_URI = BASE_URL + "accounts/kakao/callback/"
# KAKAO_CALLBACK_URI = "http://api.resumai.kr/accounts/kakao/callback/"
REST_API_KEY = env("KAKAO_REST_API_KEY")
CLIENT_SECRET = env("KAKAO_CLIENT_SECRET_KEY")

@extend_schema(exclude=True)
def kakao_login(request):
    return redirect(
        f"https://kauth.kakao.com/oauth/authorize?client_id={REST_API_KEY}&redirect_uri={KAKAO_CALLBACK_URI}&response_type=code"
    )

@extend_schema(
    summary="카카오 로그인",
    description="code를 GET 요청으로 보내면 access token, code를 반환합니다.",
    parameters=[
        OpenApiParameter(
            name="code", type=str, description="발급받은 카카오의 code 입니다."
        ),
    ],
)
@permission_classes([AllowAny])
@api_view(["GET"])
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

    data = {"access_token": access_token, "code": code}
    # TODO 유저 프로필 이미지 저장하도록
    return JsonResponse(data)


@extend_schema(
    summary="카카오 로그인 마무리",
    description="access token, code를 post 요청으로 보내면 access token, 유저 정보를 반환합니다. **(id_token은 불필요합니다.)**",
    parameters=[
        OpenApiParameter(
            name="access_token",
            type=str,
            description="발급받은 카카오의 access_token 입니다.",
        ),
        OpenApiParameter(
            name="code", type=str, description="발급받은 카카오의 code 입니다."
        ),
    ],
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "access_token": {"type": "string"},
                "code": {"type": "string"},
            },
        },
    },
    examples=[
        OpenApiExample(
            response_only=True,
            summary="Response Body Example입니다.",
            name="success_example",
            value={
                "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlI",
                "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBl",
                "user": {"pk": 6, "email": "yjoonjang@naver.com"},
            },
        ),
    ],
)
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
        user = request.user
        serializer = UserInfoUpdateSerializer(
            user, data=request.data, partial=True
        )  # 부분 업데이트 가능

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetUserInfoView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="유저 정보 반환",
    )
    def get(self, request):
        user = request.user
        serializer = GetUserInfoSerializer(user)
        return Response(serializer.data)
