# backend/notice/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # 获取系统通知与公告（登录后显示）
    path('', views.get_announcements, name='get_announcements'),
    
    # 确认已读公告
    path('/read', views.confirm_announcement_read, name='confirm_announcement_read'),
    
    # 管理员：获取所有公告
    path('/all', views.get_all_notices, name='get_all_notices'),
    
    # 管理员：创建公告
    path('/create', views.create_notice, name='create_notice'),
]