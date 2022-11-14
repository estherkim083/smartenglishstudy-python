"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # 첫번째 탭
    path('listening/', include('listeningapp.urls', namespace='listeningapp')),
    path('reading/', include('readingapp.urls', namespace='readingapp')),
    path('writing/', include('writingapp.urls', namespace='writingapp')),
    # 퀴즈 두번째 탭
    path('quiz/', include('quizapp.urls', namespace='quizapp')),
    # 어휘 및 어휘 퀴즈 탭
    path('vocab/', include('vocabapp.urls', namespace='vocabapp')),
    # 마이페이지 탭
    path('mypage/', include('mypage.urls', namespace='mypage')),
    # 유저 관리(로그인, 회원가입, 로그아웃 기능)
    path('auth/', include('users.urls', namespace='users')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
