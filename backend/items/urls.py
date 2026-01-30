# backend/items/urls.py

from django.urls import path
from . import views

urlpatterns = [

    # 6.4.1 发布失物 / 招领
    path('', views.add_item),

    # 6.4.2 物品列表查询
    path('/list', views.get_item_list),
    
    # 6.4.3 查看物品详情
    path("/detail", views.get_item_detail),

    # 6.4.4 管理员审核物品
    path('/audit', views.audit_item),

    # 6.4.5 认领物品
    path('/claim', views.add_claim),
]
