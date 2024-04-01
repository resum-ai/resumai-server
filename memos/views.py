from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiExample,
    OpenApiParameter,
)

from .serializers import PostMemoSerializer

class PostMemoView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="메모 등록",
        description="메모를 등록합니다.",
        responses={200: PostMemoSerializer},
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "content": {"type": "string"},
                },
            },
        },
    )
    def post(self, request):
        serializer = PostMemoSerializer(data=request.data)

        # 데이터 유효성 검사
        if serializer.is_valid():
            # 유효한 데이터의 경우, 메모 저장
            serializer.save(user=request.user)  # 현재 로그인한 사용자를 메모의 user 필드에 저장
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            # 데이터가 유효하지 않은 경우, 에러 메시지 반환
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)