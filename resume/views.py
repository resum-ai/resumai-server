import json

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

from resume.serializers import GenerateResumeSerializer
from resume.utils import retrieve_similar_answers
from utils.openai_call import get_chat_openai
from utils.prompts import GUIDELINE_PROMPT, GENERATE_SELF_INTRODUCTION_PROMPT


# Create your views here.
class GetGuidelinesView(APIView):
    # permission_classes = [IsAuthenticated]

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
            guideline_json = {
                "result": guideline_list
            }
            return JsonResponse(guideline_json)
        except Exception as e:
            print(e)
            error_message = {'error': '가이드라인 생성 중 오류가 발생했습니다.'}
            return JsonResponse(error_message, status=500)

class GenerateResumeView(APIView):
    # permission_classes = [IsAuthenticated]

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
                description="기업이 제시한 질문을 입력합니다.",
            ),
            OpenApiParameter(
                name="guidelines",
                type=str,
                description="가이드라인 리스트를 입력합니다.",
            ),
            OpenApiParameter(
                name="answers",
                type=str,
                description="각 가이드라인에 작성한 답안을 리스트로 전달합니다. 답변이 없을 경우, 공백을 담아 전달합니다.",
            ),
            OpenApiParameter(
                name="free_answer",
                type=str,
                description="자유 작성란에 작성한 내용을 전달합니다.",
            ),
            OpenApiParameter(
                name="favor_info",
                type=str,
                description="우대 공고에 작성한 내용을 전달합니다.",
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
        total_answer = ''

        for index, answer in enumerate(answers):
            # answer 값이 존재하는 경우에만 처리
            if answer:
                total_answer += (guidelines[index] + '\n' + answer + '\n\n')
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
            answers=total_answer,
            favor_info=favor_info,
            examples=examples_str
        )

        # 자소서 생성
        generated_self_introduction = get_chat_openai(prompt)
        generated_self_introduction_json = {
            "result": generated_self_introduction
        }

        return JsonResponse(generated_self_introduction_json)



