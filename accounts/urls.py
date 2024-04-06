from django.urls import path
from accounts import views

# TODO swagger에 뜨는 api 관리
urlpatterns = [
    path("kakao/", views.kakao_login, name="kakao_login"),
    path(
        "kakao/login/",
        views.KakaoLoginView.as_view(),
        name="kakao_login_todjango",
    ),
    path("update/", views.UpdateUserInfoView.as_view(), name="update_user_info"),
    path("user/me", views.GetUserInfoView.as_view(), name="get_user_info"),
]
