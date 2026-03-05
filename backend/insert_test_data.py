#!/usr/bin/env python
import os
import django
from datetime import datetime, timedelta

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lostfound.settings')
django.setup()

from django.utils import timezone
from items.models import Item, ItemImage, Category, Location, OperationLog as ItemOperationLog
from user.models import User
from system.models import BackupRecord


def insert_test_data():
    """插入测试数据"""
    print("开始插入测试数据...")
    
    # 创建测试用户
    test_user, created = User.objects.get_or_create(
        username='test_user',
        defaults={
            'password': 'test123',
            'real_name': '测试用户',
            'phone': '13800001111',
            'role': 1,
            'status': 1,
            'last_login_time': timezone.now() - timedelta(days=400),
            'create_time': timezone.now() - timedelta(days=500)
        }
    )
    print(f"测试用户: {test_user.username}")
    
    # 创建测试分类和地点
    category, _ = Category.objects.get_or_create(name='测试分类', parent_id=0, sort=1, status=1)
    location, _ = Location.objects.get_or_create(name='测试地点', parent_id=0, sort=1, status=1)
    
    # 1. 创建超过2天的已删除物品
    print("\n创建超过2天的已删除物品...")
    for i in range(5):
        item = Item.objects.create(
            user_id=test_user.id,
            item_type=category.id,
            item_category=1,
            name=f'测试物品 {i+1}',
            location_id=location.id,
            location_detail='测试描述',
            happen_time=timezone.now() - timedelta(days=10),
            feature='测试特征',
            reward_amount=0,
            contact_name='测试联系人',
            contact_phone='13800002222',
            current_status=0,
            create_time=timezone.now() - timedelta(days=10),
            update_time=timezone.now() - timedelta(days=5)
        )
        print(f"  创建物品: {item.name}")
    
    # 2. 创建超过90天的操作日志
    print("\n创建超过90天的操作日志...")
    for i in range(10):
        log = ItemOperationLog.objects.create(
            user_id=test_user.id,
            user_role=1,
            module='item',
            operation='create',
            related_id=i+1,
            content=f'测试操作日志 {i+1}',
            ip_address='127.0.0.1',
            operation_time=timezone.now() - timedelta(days=100)
        )
        print(f"  创建日志: {log.id}")
    
    # 3. 创建超过7天的备份记录
    print("\n创建超过7天的备份记录...")
    for i in range(3):
        backup = BackupRecord.objects.create(
            name=f'测试备份 {i+1}',
            backup_type='full',
            file_path=f'/tmp/backup_{i+1}.json',
            file_size=1024 * 1024 * 50,
            tables=['users', 'items', 'records'],
            status='completed',
            created_by=test_user.id,
            created_time=timezone.now() - timedelta(days=10),
            completed_time=timezone.now() - timedelta(days=9)
        )
        print(f"  创建备份: {backup.name}")
    
    # 4. 创建一些孤儿图片
    print("\n创建孤儿图片...")
    for i in range(5):
        image = ItemImage.objects.create(
            item_id=99999,
            image_data=b'test',
            image_url=f'test_image_{i+1}.jpg',
            image_type=1,
            sort=i,
            create_time=timezone.now() - timedelta(days=30)
        )
        print(f"  创建图片: {image.id}")
    
    # 5. 创建未激活账号
    print("\n创建未激活账号...")
    for i in range(3):
        user = User.objects.create(
            username=f'inactive_user_{i+1}',
            password='test123',
            real_name=f'未激活用户 {i+1}',
            phone=f'1380000{i+1:02d}{i+1:02d}',
            role=1,
            status=1,
            last_login_time=timezone.now() - timedelta(days=400),
            create_time=timezone.now() - timedelta(days=500)
        )
        print(f"  创建用户: {user.username}")
    
    print("\n测试数据插入完成！")
    print("\n清理统计应该显示:")
    print("- 已删除物品: 5条")
    print("- 过期日志: 10条")
    print("- 失效备份: 3个")
    print("- 孤儿图片: 5条")
    print("- 未激活账号: 4个")


if __name__ == '__main__':
    insert_test_data()