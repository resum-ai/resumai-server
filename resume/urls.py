from django.urls import path
from resume import views


urlpatterns = [
    path("guidelines/", views.GetGuidelinesView.as_view(), name="get_guidelines"),
    path("generate/", views.GenerateResumeView.as_view(), name="generate_resume"),
    path("", views.PostResumeView.as_view(), name="post_resume"),
]
