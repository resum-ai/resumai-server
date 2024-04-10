from django.urls import path
from resume import views


urlpatterns = [
    path("/all", views.GetAllResumeView.as_view(), name="get_all_resume"),
    path("/guidelines", views.GetGuidelinesView.as_view(), name="get_guidelines"),
    path("/generate", views.GenerateResumeView.as_view(), name="generate_resume"),
    # path("", views.PostResumeView.as_view(), name="post_resume"),
    path("/update/<int:id>", views.UpdateResumeView.as_view(), name="update_resume"),
    path("/scrap/<int:id>", views.ScrapResumeView.as_view(), name="scrap_resume"),
    path("/chat", views.ChatView.as_view(), name="chat"),
    path("/<int:pk>", views.GetResumeView.as_view(), name="update_resume"),
]
