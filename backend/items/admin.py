from django.contrib import admin
from .models import Item


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    """
    物品信息后台管理
    """
    # 后台列表页显示的字段（字段名必须存在于模型中）
    list_display = (
        'id',
        'name',
        'item_category',
        'current_status',
        'create_time',
    )

    # 右侧过滤器
    list_filter = (
        'item_category',
        'current_status',
    )

    # 搜索框
    search_fields = (
        'name',
        'feature',
    )

    # 每页显示数量
    list_per_page = 20
