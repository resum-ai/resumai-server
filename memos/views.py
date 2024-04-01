from django.shortcuts import render

# Create your views here.
from django.urls import path
from memos import views

# TODO swagger에 뜨는 api 관리
urlpatterns = [
    path("kakao/login/", views.kakao_login, name="kakao_login"),
]
