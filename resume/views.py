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
from resume.serializers import GenerateResumeSerializer, PostResumeSerializer, UpdateResumeSerializer
from resume.utils import retrieve_similar_answers
from utils.openai_call import get_chat_openai
from utils.prompts import GUIDELINE_PROMPT, GENERATE_SELF_INTRODUCTION_PROMPT


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
            print(e)
            error_message = {"error": "가이드라인 생성 중 오류가 발생했습니다."}
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
        print(question)

        # 답변을 guideline + answer + free_answer로 구성
        total_answer = ""
        print(answers)
        for index, answer in enumerate(answers):
            # answer 값이 존재하는 경우에만 처리
            if answer:
                total_answer += guidelines[index] + "\n" + answer + "\n\n"
        if free_answer:
            total_answer += free_answer

        # 예시 retrieve
        examples = retrieve_similar_answers(total_answer)
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

        return JsonResponse(generated_self_introduction_json)

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
        print(request.user)
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
        resume_id = kwargs.get('id')  # URL에서 resume의 id를 가져옵니다.

        try:
            resume = Resume.objects.get(id=resume_id, user=user)  # 요청한 사용자의 resume만 선택
        except Resume.DoesNotExist:
            return Response({'error': 'Resume not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = PostResumeSerializer(
            resume, data=request.data, partial=True
        )  # 업데이트 대상 인스턴스를 지정하고 부분 업데이트 가능

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)