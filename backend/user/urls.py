from django.urls import path
from . import views

urlpatterns = [
    # 6.3.1 用户登录
    path('/login', views.login_user, name='login_user'),  # POST /api/user/login
]