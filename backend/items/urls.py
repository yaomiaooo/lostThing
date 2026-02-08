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

    # 6.4.6 上传物品图片（图片存 MySQL）
    path('/image/upload', views.upload_item_image),

    # 6.4.7 获取分类树
    path('/category/tree', views.get_category_tree),

    # 6.4.8 获取地点树
    path('/location/tree', views.get_location_tree),

    # 6.4.9 获取物品图片
    path('/image/<int:image_id>', views.get_item_image),

    # 6.4.10 获取当前用户的发布记录
    path('/my-posts', views.get_my_posts),
    # 6.4.11 修改物品信息   
    path('/<int:item_id>', views.update_item, name='update_item'),
    # 6.4.12 取消发布物品
    path('/<int:item_id>/cancel', views.cancel_item, name='cancel_item'),
    # 6.4.13 删除物品
    path('/<int:item_id>/delete', views.delete_item, name='delete_item'),

]
