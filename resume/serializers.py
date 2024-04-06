from rest_framework import serializers


class GenerateResumeSerializer(serializers.Serializer):
    question = serializers.CharField()
    guidelines = serializers.CharField()
    answers = serializers.CharField()
    free_answer = serializers.CharField()
    favor_info = serializers.CharField()
