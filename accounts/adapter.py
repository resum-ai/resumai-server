from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


class CustomKakaoOAuth2Adapter(OAuth2Adapter):
    access_token_url = "https://kauth.kakao.com/oauth/token"
    authorize_url = "https://kauth.kakao.com/oauth/authorize"
    profile_url = "https://kapi.kakao.com/v2/user/me"

    def complete_login(self, request, app, token, **kwargs):
        headers = {"Authorization": "Bearer {0}".format(token.token)}
        resp = (
            get_adapter().get_requests_session().get(self.profile_url, headers=headers)
        )
        resp.raise_for_status()
        extra_data = resp.json()
        print(extra_data)
        return self.get_provider().sociallogin_from_response(request, extra_data)
