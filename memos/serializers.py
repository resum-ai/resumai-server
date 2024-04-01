from rest_framework import serializers
from .models import Memo


class MemoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Memo
        fields = '__all__'  # 모든 필드를 포함

class PostMemoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Memo
        fields = ("id", "title", "content", "created_at", "updated_at", "is_scrapped", "is_finished")
        read_only_fields = ("id", "created_at", "updated_at")