from django.db import models
from django.conf import settings


class Resume(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)  # 제목이 곧 지원하려는 기업명과 동일함
    position = models.CharField(max_length=255)  # 지원하려는 기업의 지원하려는 직무
    question = models.TextField()  # 작성하려는 자소서에서 답변할 질문
    content = models.TextField()  # 질문에 대한 답변 = contents
    due_date = models.DateField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_finished = models.BooleanField(default=False)
    is_liked = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class ChatHistory(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE)
    query = models.TextField(null=True)  # 사용자의 질문
    response = models.TextField(null=True)  # 챗봇의 응답
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
