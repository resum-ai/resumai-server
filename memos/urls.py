from django.urls import path
from memos import views


urlpatterns = [
    path("", views.PostMemoView.as_view(), name="post_memo"),
]
