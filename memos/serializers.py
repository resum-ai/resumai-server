from rest_framework import serializers
from .models import Memo


class PostMemoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Memo
        fields = ("id", "title", "content", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")