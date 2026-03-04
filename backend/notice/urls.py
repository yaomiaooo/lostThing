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

     # ==================== 新增：管理员公告管理接口 ====================
    
    # 获取公告管理列表（支持筛选）
    path('/admin/list', views.get_admin_announcement_list, name='get_admin_announcement_list'),
    
    # 发布公告（全局公告）
    path('/admin', views.publish_announcement, name='publish_announcement'),
    
    # 修改公告
    path('/admin/<int:announcement_id>', views.update_announcement, name='update_announcement'),
    
    # 删除公告
    path('/admin/<int:announcement_id>/delete', views.delete_announcement, name='delete_announcement'),
    
    # ==================== 新增：站内通知接口 ====================
    
    # 发送站内通知
    path('/notifications/admin', views.send_system_notification, name='send_system_notification'),
    
    # 获取通知发送历史
    path('/notifications/admin/history', views.get_notification_history, name='get_notification_history'),
]