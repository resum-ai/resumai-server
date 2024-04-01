from django.urls import path
from memos import views


urlpatterns = [
    path("", views.PostMemoView.as_view(), name="post_memo"),
    path("all", views.GetAllMemoView.as_view(), name="get_all_memos")
]
