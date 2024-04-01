from django.urls import path
from memos import views


urlpatterns = [
    path("", views.PostMemoView.as_view(), name="post_memo"),
    path("all", views.GetAllMemoView.as_view(), name="get_all_memos"),
    path('memo/<int:pk>/', views.GetMemoDetailView.as_view(), name='memo-detail'),
    # path('scrap/<int:pk>/', views.ScrapMemoView.as_view(), name='scrap-memo'),
    path('delete/<int:pk>/', views.DeleteMemoView.as_view(), name='delete-memo'),
]
