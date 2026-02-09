from django.urls import path
from . import views

urlpatterns = [
    # 6.5.1 进入聊天会话
    path('/conversation/enter', views.enter_conversation, name='enter_conversation'),
    # 6.5.2 获取会话消息列表
    path('/conversation/messages', views.get_conversation_messages, name='get_conversation_messages'),
    # 6.5.3 发送消息
    path('/conversation/message/send', views.send_message, name='send_message'),
]