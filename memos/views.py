from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from django.http import Http404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination


from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiExample,
    OpenApiParameter,
)

from .models import Memo
from .serializers import PostMemoSerializer, MemoSerializer


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


class GetAllMemoView(APIView, PageNumberPagination):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # 현재 인증된 유저에게 속한 메모들을 조회
        memos = Memo.objects.filter(user=request.user)

        # Pagination 적용
        page = self.paginate_queryset(memos, request, view=self)
        if page is not None:
            serializer = MemoSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        # Pagination이 적용되지 않은 경우(선택적)
        serializer = MemoSerializer(memos, many=True)
        return Response(serializer.data)


class GetMemoDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        try:
            memo = Memo.objects.get(pk=pk)
            # 메모를 작성한 유저와 현재 요청 유저가 동일한지 확인
            if memo.user != user:
                raise Http404("해당 메모에 접근할 권한이 없습니다.")
            return memo
        except Memo.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        memo = self.get_object(pk, request.user)
        serializer = MemoSerializer(memo)
        return Response(serializer.data, status=status.HTTP_200_OK)


# class ScrapMemoView(APIView):
#     permission_classes = [IsAuthenticated]
#
#     def get_object(self, pk, user):
#         try:
#             memo = Memo.objects.get(pk=pk)
#             # 메모를 작성한 유저와 현재 요청 유저가 동일한지 확인
#             if memo.user != user:
#                 raise Http404("해당 메모를 스크랩할 권한이 없습니다.")
#             return memo
#         except Memo.DoesNotExist:
#             raise Http404
#
#     def get(self, request, pk, format=None):
#         memo = self.get_object(pk, request.user)
#         # is_scrapped 값 토글
#         memo.is_scrapped = not memo.is_scrapped
#         memo.save(update_fields=['is_scrapped'])
#         return Response({'status': 'success', 'is_scrapped': memo.is_scrapped}, status=status.HTTP_200_OK)

class DeleteMemoView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        try:
            memo = Memo.objects.get(pk=pk)
            # 메모를 작성한 유저와 현재 요청 유저가 동일한지 확인
            if memo.user != user:
                raise Http404("You do not have permission to delete this memo.")
            return memo
        except Memo.DoesNotExist:
            raise Http404

    def delete(self, request, pk, format=None):
        memo = self.get_object(pk, request.user)
        memo.delete()
        return Response({'status': 'success', 'message': 'Memo deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)