from rest_framework import serializers

from resume.models import Resume, ChatHistory


class GenerateResumeSerializer(serializers.Serializer):
    title = serializers.CharField()
    position = serializers.CharField()
    company = serializers.CharField()
    due_date = serializers.CharField()
    question = serializers.CharField()
    guidelines = serializers.ListField(child=serializers.CharField())
    answers = serializers.ListField(child=serializers.CharField())
    free_answer = serializers.CharField()
    favor_info = serializers.CharField()


class PostResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = (
            "title",
            "position",
            "company",
            "question",
            "content",
            "due_date",
            "created_at",
            "updated_at",
            "is_finished",
            "is_liked",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class UpdateResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = (
            "id",
            "title",
            "position",
            "content",
            "due_date",
            "created_at",
            "updated_at",
            "is_finished",
            "is_liked",
        )
        read_only_fields = ("created_at", "updated_at")


class ChatHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatHistory
        fields = ("query", "response", "created_at")
