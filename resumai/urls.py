from django.contrib import admin
from django.urls import include, path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from accounts.urls import urlpatterns as accounts_urlpatterns
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from .views import kakao_login_page

schema_view = get_schema_view(
    openapi.Info(
        title="Break-Magazine API",
        default_version="v1",
        description="API documentation for Break-Magazine Webzine project",
    ),
    public=True,
    patterns=accounts_urlpatterns,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path("", kakao_login_page, name="home"),
    path("admin/", admin.site.urls),
    path("accounts/", include("dj_rest_auth.urls")),
    # path('accounts/', include('allauth.urls')),
    path("accounts/", include("accounts.urls")),
    # path('accounts/', include('dj_rest_auth.urls')),
    # path(
    #     "accounts/social/",
    #     include("allauth.socialaccount.urls"),
    # ),
    # path("registration/", include("dj_rest_auth.registration.urls")),
    # swagger 관련
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]
