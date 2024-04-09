import json
import logging

from django.http import Http404
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework import serializers
from django.http import JsonResponse
from typing import List

from drf_spectacular.utils import (
    extend_schema,
    inline_serializer,
    OpenApiParameter,
)

from resume.models import Resume
from resume.serializers import (
    GenerateResumeSerializer,
    PostResumeSerializer,
    UpdateResumeSerializer,
)
from resume.utils import retrieve_similar_answers, run_llm
from utils.openai_call import get_chat_openai
from utils.prompts import GUIDELINE_PROMPT, GENERATE_SELF_INTRODUCTION_PROMPT


class GetAllResumeView(APIView, PageNumberPagination):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="전체 자기소개서를 받아옵니다.",
        description="사용자가 작성한 전체 자기소개서를 받아옵니다.",
        responses={
            200: inline_serializer(
                name="GetAllResumeResponse",
                fields={
                    "count": serializers.IntegerField(),
                    "next": serializers.URLField(),
                    "previous": serializers.URLField(),
                    "results": PostResumeSerializer(many=True),
                },
            )
        },
    )
    def get(self, request):
        # 현재 인증된 유저에게 속한 메모들을 조회
        resumes = Resume.objects.filter(user=request.user)

        # Pagination 적용
        page = self.paginate_queryset(resumes, request, view=self)
        if page is not None:
            serializer = PostResumeSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        # Pagination이 적용되지 않은 경우(선택적)
        serializer = PostResumeSerializer(resumes, many=True)
        return Response(serializer.data)


# Create your views here.
class GetGuidelinesView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="가이드라인 생성",
        description="질문을 기반으로 가이드라인을 생성합니다.",
        # responses={
        #     200: inline_serializer(
        #         name="GetGuidelineResponse",
        #         fields={
        #             "results": ['guide1', 'guide2', 'guide3']
        #         }
        #     )
        # },
        parameters=[
            OpenApiParameter(
                name="question",
                type=str,
                description="기업이 제시한 질문을 입력합니다.",
            )
        ],
    )
    def get(self, request):
        question = request.GET.get("question")
        try:
            prompt = GUIDELINE_PROMPT.format(question=question)
            guideline_string = get_chat_openai(prompt)
            guideline_list = json.loads(guideline_string.replace("'", '"'))
            guideline_json = {"result": guideline_list}
            return JsonResponse(guideline_json)
        except Exception as e:
            error_message = {"error": "가이드라인 생성 중 오류가 발생했습니다. 질문을 올바르게 입력해 주세요."}
            return JsonResponse(error_message, status=500)


class GenerateResumeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="자기소개서 생성",
        description="답변을 기반으로 자기소개서를 생성합니다.",
        responses={
            200: inline_serializer(
                name="GenerateResumeResponse",
                fields={
                    "result": serializers.CharField(),
                },
            )
        },
        parameters=[
            OpenApiParameter(
                name="question",
                type=str,
                description="기업이 제시한 질문",
            ),
            OpenApiParameter(
                name="guidelines",
                type={"type": "array", "items": {"type": "string"}},
                location=OpenApiParameter.QUERY,
                required=False,
                style="form",
                explode=False,
                description="제공된 가이드라인",
            ),
            OpenApiParameter(
                name="answers",
                type={"type": "array", "items": {"type": "string"}},
                location=OpenApiParameter.QUERY,
                required=False,
                style="form",
                explode=False,
                description="제공된 가이드라인에 대한 답변",
            ),
            OpenApiParameter(
                name="free_answer",
                type=str,
                description="자유 작성란에 작성한 답변",
            ),
            OpenApiParameter(
                name="favor_info",
                type=str,
                description="우대사항",
            ),
        ],
    )
    def get(self, request):
        question = request.GET.get("question")
        guidelines = request.GET.get("guidelines")
        answers = request.GET.get("answers")
        free_answer = request.GET.get("free_answer")
        favor_info = request.GET.get("favor_info")

        # 답변을 guideline + answer + free_answer로 구성
        total_answer = ""
        for index, answer in enumerate(answers):
            # answer 값이 존재하는 경우에만 처리
            if answer:
                total_answer += guidelines[index] + "\n" + answer + "\n\n"
        if free_answer:
            total_answer += free_answer

        # 예시 retrieve
        examples = retrieve_similar_answers(total_answer)
        if len(examples) == 0:
            error_message = {"error": "유사한 질문을 가져오는 도중 문제가 발생했습니다. 다시 시도해 주세요."}
            return JsonResponse(error_message, status=500)

        examples_str = "\n\n".join(
            [
                f"예시{i}) \nQuestion: {ex['metadata']['question']} \nAnswer: {ex['metadata']['answer']}"
                for i, ex in enumerate(examples, start=1)
            ]
        )

        # 프롬프트 작성
        prompt = GENERATE_SELF_INTRODUCTION_PROMPT.format(
            question=question,
            answer=total_answer,
            favor_info=favor_info,
            examples=examples_str,
        )

        # 자소서 생성
        generated_self_introduction = get_chat_openai(prompt)
        generated_self_introduction_json = {"result": generated_self_introduction}

        return JsonResponse(generated_self_introduction_json, status=200)


class PostResumeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="자기소개서 등록",
        description="자기소개서를 등록합니다.",
        responses={200: PostResumeSerializer},
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "position": {"type": "string"},
                    "content": {"type": "string"},
                    "due_date": {"type": "string"},
                },
            },
        },
    )
    def post(self, request):
        serializer = PostResumeSerializer(data=request.data)

        # 데이터 유효성 검사
        if serializer.is_valid():
            # 유효한 데이터의 경우, 자소서 저장
            serializer.save(
                user=request.user
            )  # 현재 로그인한 사용자를 메모의 user 필드에 저장
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            # 데이터가 유효하지 않은 경우, 에러 메시지 반환
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateResumeView(APIView):
    permission_classes = [IsAuthenticated]  # 인증된 사용자만 접근 가능하도록 설정

    @extend_schema(
        summary="자기소개서 업데이트",
        request=UpdateResumeSerializer,
        responses={200: PostResumeSerializer},
    )
    def put(self, request, *args, **kwargs):
        user = request.user
        resume_id = kwargs.get("id")  # URL에서 resume의 id를 가져옵니다.

        try:
            resume = Resume.objects.get(
                id=resume_id, user=user
            )  # 요청한 사용자의 resume만 선택
        except Resume.DoesNotExist:
            return Response(
                {"error": "Resume not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = PostResumeSerializer(
            resume, data=request.data, partial=True
        )  # 업데이트 대상 인스턴스를 지정하고 부분 업데이트 가능

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ScrapResumeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        resume_id = kwargs.get("id", None)  # URL로부터 자기소개서 id를 받아옵니다.
        if not resume_id:
            return Response(
                {"error": "Resume ID is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            resume = Resume.objects.get(id=resume_id)
            # is_liked 필드의 값을 반전시킵니다.
            resume.is_liked = not resume.is_liked
            resume.save(
                update_fields=["is_liked"]
            )  # 업데이트할 필드를 명시적으로 지정합니다.

            return Response(
                {"id": resume_id, "is_liked": resume.is_liked},
                status=status.HTTP_200_OK,
            )
        except Resume.DoesNotExist:
            return Response(
                {"error": "Resume not found"}, status=status.HTTP_404_NOT_FOUND
            )

class ChatView(APIView):

    @extend_schema(
        summary="챗봇 대화",
        description="챗봇과의 대화를 통해 자기소개서를 업데이트합니다.",
        responses={200: PostResumeSerializer},
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "position": {"type": "string"},
                    "content": {"type": "string"},
                    "due_date": {"type": "string"},
                },
            },
        },
    )
    def post(self, request):
        query = request.data.query
        langchain_answer = run_llm(query=query)

        return Response(
            {"answer": langchain_answer},
            status=status.HTTP_200_OK,
        )