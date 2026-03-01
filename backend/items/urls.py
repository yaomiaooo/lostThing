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
    # 6.4.14 更新物品图片
    path('/<int:item_id>/images/update', views.update_item_images, name='update_item_images'),

    # ==================== 新增管理员接口 ====================
    
    # 6.4.15 获取审核历史记录（增强版，支持多种筛选）
    path('/audit/history', views.get_audit_history, name='get_audit_history'),
    
    # 6.4.16 更新物品状态（已认领、已归档等）
    path('/<int:item_id>/status', views.update_item_status, name='update_item_status'),
    
    # 6.4.17 获取长期无人认领物品列表
    path('/unclaimed/long-term', views.get_long_term_unclaimed, name='get_long_term_unclaimed'),
    
    # 6.4.18 归档单个物品
    path('/<int:item_id>/archive', views.archive_item, name='archive_item'),
    
    # 6.4.19 批量归档物品
    path('/batch/archive', views.batch_archive_items, name='batch_archive_items'),
    
    # 6.4.20 获取统计数据
    path('/statistics/overview', views.get_statistics, name='get_statistics'),
    
    # 6.4.21 导出统计数据
    path('/statistics/export', views.export_statistics, name='export_statistics'),
    
    # 6.4.22 管理员专用物品列表（支持多种条件查询）
    path('/admin/list', views.admin_item_list, name='admin_item_list'),
    
    # 6.4.23 获取认领申请列表
    path('/claim/list', views.get_claim_list, name='get_claim_list'),
    
    # 6.4.24 审核认领申请
    path('/claim/<int:claim_id>/audit', views.audit_claim, name='audit_claim'),

     # ==================== 新增：分类管理接口（管理员） ====================
    
    # 获取分类树（管理视角，包含禁用分类）
    path('/admin/category/tree', views.get_admin_category_tree, name='get_admin_category_tree'),
    
    # 新增分类
    path('/admin/category', views.create_category, name='create_category'),
    
    # 修改分类
    path('/admin/category/<int:category_id>', views.update_category, name='update_category'),
    
    # 删除分类
    path('/admin/category/<int:category_id>/delete', views.delete_category, name='delete_category'),
    
    # ==================== 新增：地点管理接口（管理员） ====================
    
    # 获取地点树（管理视角，包含禁用地点）
    path('/admin/location/tree', views.get_admin_location_tree, name='get_admin_location_tree'),
    
    # 新增地点
    path('/admin/location', views.create_location, name='create_location'),
    
    # 修改地点
    path('/admin/location/<int:location_id>', views.update_location, name='update_location'),
    
    # 删除地点
    path('/admin/location/<int:location_id>/delete', views.delete_location, name='delete_location'),
]
