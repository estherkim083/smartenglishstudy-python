from django.urls import path
from .views import Register, Login, Logout, SocialLogin, SocialRegister, NaverRegister, NaverLogin


app_name = 'users'

urlpatterns = [
    path('', Login.as_view(), name="login-user"),
    path('register/', Register.as_view(), name="create-user"),
    path('social-register/', SocialRegister.as_view(), name="social-create-user"),
    path('social-login/', SocialLogin.as_view(), name='social-login'),
    path('logout/<str:email>', Logout.as_view(),
         name='logout_user'),
    path('naver-register/', NaverRegister.as_view(), name='naver-register-with-token'),
    path('naver-login/', NaverLogin.as_view(), name='naver-login-with-token')
]