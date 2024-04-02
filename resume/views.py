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

from utils.openai_call import get_chat_openai
from utils.prompts import GUIDELINE_PROMPT


# Create your views here.
class GetGuidelinesView(APIView):
    @extend_schema(
        summary="메모 검색",
        description="키워드를 기반으로 메모를 검색합니다.",
        responses={
            200: ["가이드라인1", "가이드라인2"]
        },
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
            guideline_json = json.loads(guideline_string.replace("'", '"'))
            print(guideline_json)
            return JsonResponse(guideline_json, safe=False)
        except Exception as e:
            print(e)
            error_message = {'error': '가이드라인 생성 중 오류가 발생했습니다.'}
            return JsonResponse(error_message, status=500)
