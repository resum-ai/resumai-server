from django.shortcuts import render


def kakao_login_page(request):
    return render(request, "home.html")