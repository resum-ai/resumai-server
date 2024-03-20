from django.urls import path
from accounts import views

urlpatterns = [
    path("kakao/login/", views.kakao_login, name="kakao_login"),
    path("kakao/callback/", views.kakao_callback, name="kakao_callback"),
    path(
        "kakao/login/finish/",
        views.KakaoLoginView.as_view(),
        name="kakao_login_todjango",
    ),
    path("join/", views.UpdateUserInfoView.as_view(), name="update_user_info"),
    path("user/me", views.GetUserInfoView.as_view(), name="get_user_info"),
]
