from django.http import Http404
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework import serializers
from django.http import JsonResponse

from drf_spectacular.utils import (
    extend_schema,
    inline_serializer,
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
            serializer.save(
                user=request.user
            )  # 현재 로그인한 사용자를 메모의 user 필드에 저장
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            # 데이터가 유효하지 않은 경우, 에러 메시지 반환
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetAllMemoView(APIView, PageNumberPagination):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="전체 메모를 받아옵니다.",
        description="사용자가 작성한 전체 메모를 받아옵니다.",
        responses={
            200: inline_serializer(
                name="GetAllMemoResponse",
                fields={
                    "count": serializers.IntegerField(),
                    "next": serializers.URLField(),
                    "previous": serializers.URLField(),
                    "results": MemoSerializer(many=True),
                },
            )
        },
    )
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

    @extend_schema(
        summary="특정 메모를 받아옵니다.",
        description="사용자가 작성한 특정 메모의 디테일 받아옵니다.",
        responses={200: MemoSerializer},
    )
    def get(self, request, pk, format=None):
        memo = self.get_object(pk, request.user)
        serializer = MemoSerializer(memo)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DeleteMemoView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        try:
            memo = Memo.objects.get(pk=pk)
            # 메모를 작성한 유저와 현재 요청 유저가 동일한지 확인
            if memo.user != user:
                raise Http404("해당 메모를 제거할 자격이 없습니다.")
            return memo
        except Memo.DoesNotExist:
            raise Http404

    @extend_schema(
        summary="메모 삭제",
        description="특정 메모를 삭제합니다. 메모를 작성한 사용자만 해당 메모를 삭제할 수 있습니다.",
        responses={
            204: None,  # 성공적으로 삭제되었을 때, 특별한 응답 본문은 없음
            404: {"description": "해당 메모를 찾을 수 없거나 삭제할 권한이 없습니다."},
        },
    )
    def delete(self, request, pk, format=None):
        memo = self.get_object(pk, request.user)
        memo.delete()
        return JsonResponse(
            {"status": "success", "message": "Memo deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )


class CustomPagination(PageNumberPagination):
    # 클라이언트로부터 'size' 파라미터를 받아 페이지 크기를 결정
    page_size_query_param = "size"

    # 'size' 파라미터가 제공되지 않은 경우 기본 페이지 크기
    def get_page_size(self, request):
        return super().get_page_size(request)

class UpdateMemoView(APIView):
    permission_classes = [IsAuthenticated]  # 인증된 사용자만 접근 가능하도록 설정

    @extend_schema(
        summary="자기소개서 업데이트",
        request=PostMemoSerializer,
        responses={200: PostMemoSerializer},
    )
    def put(self, request, *args, **kwargs):
        user = request.user
        resume_id = kwargs.get('id')  # URL에서 resume의 id를 가져옵니다.

        try:
            resume = Memo.objects.get(id=resume_id, user=user)  # 요청한 사용자의 resume만 선택
        except Memo.DoesNotExist:
            return Response({'error': 'Resume not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = PostMemoSerializer(
            resume, data=request.data, partial=True
        )  # 업데이트 대상 인스턴스를 지정하고 부분 업데이트 가능

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SearchMemoView(APIView, CustomPagination):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="메모 검색",
        description="키워드를 기반으로 메모를 검색합니다.",
        responses={
            200: inline_serializer(
                name="SearchResponse",
                fields={
                    "count": serializers.IntegerField(),
                    "next": serializers.URLField(),
                    "previous": serializers.URLField(),
                    "results": PostMemoSerializer(many=True),
                },
            )
        },
        parameters=[
            OpenApiParameter(
                name="keyword",
                type=str,
                description="검색할 키워드입니다.",
            ),
            OpenApiParameter(
                name="page", type=int, description="한번에 요청할 page 사이즈 입니다."
            ),
            OpenApiParameter(
                name="size", type=int, description="한 화면에 표시할 메모의 개수입니다."
            ),
        ],
    )
    def get(self, request):
        keyword = request.query_params.get("keyword", "")

        query_set = Memo.objects.filter(
            Q(user=request.user)
            & (Q(title__icontains=keyword) | Q(content__icontains=keyword))
        )

        page = self.paginate_queryset(query_set, request, view=self)
        if page is not None:
            serializer = MemoSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        # Pagination이 적용되지 않는 경우의 대비책(예: size 파라미터 누락 등)
        serializer = MemoSerializer(query_set, many=True)
        return Response(serializer.data)
