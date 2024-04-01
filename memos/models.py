from django.db import models
from django.conf import settings
from django.utils import timezone


class Memo(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)
    is_scrapped = models.BooleanField()
    is_finished = models.BooleanField()
    # TODO: 메모 스크랩 가능해야 하고, 작성중인지 여부도 필요
    def __str__(self):
        return self.title
