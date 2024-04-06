from django.db import models
from django.conf import settings


class Resume(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)  # 제목이 곧 지원하려는 기업명과 동일함
    position = models.CharField(max_length=255)  # 지원하려는 기업의 지원하려는 직무
    content = models.TextField()
    due_date = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_finished = models.BooleanField(default=False)
    is_liked = models.BooleanField(default=False)

    def __str__(self):
        return self.title
