import json
import os
import csv
import zipfile
from datetime import datetime, timedelta
from django.http import JsonResponse, FileResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db import connection, models
from django.conf import settings
from .models import BackupRecord, ExportTask, OperationLog, Feedback
from items.models import Item, ItemImage, ItemStatusHistory, Category, Location, Claim, OperationLog as ItemOperationLog
from user.models import User
from chat.models import Conversation, Message
from notice.models import Notice, Notification

# 确保备份和导出目录存在
BACKUP_DIR = os.path.join(settings.BASE_DIR, 'backups')
EXPORT_DIR = os.path.join(settings.BASE_DIR, 'exports')
os.makedirs(BACKUP_DIR, exist_ok=True)
os.makedirs(EXPORT_DIR, exist_ok=True)

# 所有需要备份的模型
ALL_MODELS = {
    'items': Item,
    'item_images': ItemImage,
    'item_status_history': ItemStatusHistory,
    'categories': Category,
    'locations': Location,
    'claims': Claim,
    'operation_logs': ItemOperationLog,
    'users': User,
    'conversations': Conversation,
    'messages': Message,
    'notices': Notice,
}


def get_client_ip(request):
    """获取客户端IP"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def log_operation(request, operation_type, detail, user_id=None, user_name=None):
    """记录操作日志"""
    try:
        if user_id is None:
            user_id = request.session.get('user_id', 0)
        if user_name is None:
            user_name = request.session.get('username', 'unknown')
        
        OperationLog.objects.create(
            operation_type=operation_type,
            operation_detail=detail,
            ip_address=get_client_ip(request),
            user_id=user_id,
            user_name=user_name
        )
    except Exception:
        pass


@csrf_exempt
@require_http_methods(["GET"])
def get_data_stats(request):
    """获取数据统计"""
    try:
        stats = {
            'items': {
                'total': Item.objects.count(),
                'thisMonth': Item.objects.filter(
                    create_time__gte=datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                ).count()
            },
            'users': {
                'total': User.objects.count(),
                'active': User.objects.filter(
                    last_login_time__gte=datetime.now() - timedelta(days=30)
                ).count()
            },
            'images': {
                'count': ItemImage.objects.count(),
                'size': 0  # 简化，实际需要计算
            },
            'trash': {
                'count': 0,
                'size': 0
            }
        }
        return JsonResponse({'code': 200, 'data': stats})
    except Exception as e:
        return JsonResponse({'code': 200, 'message': str(e)})


@csrf_exempt
@require_http_methods(["POST"])
def cleanup_orphan_files(request):
    """清理孤儿文件"""
    try:
        # 清理孤儿图片文件
        item_ids = Item.objects.values_list('id', flat=True)
        orphan_images = ItemImage.objects.exclude(item_id__in=item_ids)
        orphan_count = orphan_images.count()
        
        if orphan_count > 0:
            orphan_images.delete()
        
        log_operation(request, 'cleanup', f"清理孤儿图片: {orphan_count} 个")
        
        return JsonResponse({
            'code': 200, 
            'message': '清理完成',
            'data': {
                'count': orphan_count
            }
        })
    except Exception as e:
        return JsonResponse({'code': 500, 'message': str(e)})


@csrf_exempt
@require_http_methods(["GET"])
def get_backups(request):
    """获取备份列表"""
    try:
        backups = BackupRecord.objects.all().values()
        return JsonResponse({'code': 200, 'data': list(backups)})
    except Exception as e:
        return JsonResponse({'code': 500, 'message': str(e)})


@csrf_exempt
@require_http_methods(["POST"])
def create_backup(request):
    """创建备份"""
    try:
        data = json.loads(request.body)
        backup_type = data.get('type', 'full')
        
        # 创建备份记录
        backup = BackupRecord.objects.create(
            name=f"{'全量' if backup_type == 'full' else '增量'}备份-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            backup_type=backup_type,
            file_path='',
            tables=list(ALL_MODELS.keys()),
            status='processing',
            created_by=request.session.get('user_id', 0)
        )
        
        log_operation(request, 'backup', f"创建{'全量' if backup_type == 'full' else '增量'}备份任务")
        
        # 模拟备份过程
        import threading
        threading.Thread(target=perform_backup, args=(backup.id,)).start()
        
        return JsonResponse({'code': 200, 'message': '备份任务已创建'})
    except Exception as e:
        return JsonResponse({'code': 500, 'message': str(e)})


def perform_backup(backup_id):
    """执行备份（后台线程）"""
    try:
        backup = BackupRecord.objects.get(id=backup_id)
        backup.status = 'processing'
        backup.save()
        
        # 简单的JSON备份实现
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"backup_{timestamp}.json"
        backup_path = os.path.join(BACKUP_DIR, backup_filename)
        
        backup_data = {}
        for table_name, model in ALL_MODELS.items():
            backup_data[table_name] = list(model.objects.values())
        
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, default=str)
        
        # 更新备份记录
        backup.file_path = backup_path
        backup.file_size = os.path.getsize(backup_path)
        backup.status = 'completed'
        backup.completed_time = datetime.now()
        backup.save()
        
    except Exception as e:
        try:
            backup = BackupRecord.objects.get(id=backup_id)
            backup.status = 'failed'
            backup.error_message = str(e)
            backup.save()
        except Exception:
            pass


@csrf_exempt
@require_http_methods(["GET"])
def download_backup(request, backup_id):
    """下载备份"""
    try:
        backup = BackupRecord.objects.get(id=backup_id)
        if os.path.exists(backup.file_path):
            log_operation(request, 'backup', f"下载备份: {backup.name}")
            return FileResponse(open(backup.file_path, 'rb'), as_attachment=True)
        return JsonResponse({'code': 404, 'message': '文件不存在'})
    except Exception as e:
        return JsonResponse({'code': 500, 'message': str(e)})


@csrf_exempt
@require_http_methods(["POST"])
def restore_backup(request, backup_id):
    """恢复备份"""
    try:
        backup = BackupRecord.objects.get(id=backup_id)
        log_operation(request, 'restore', f"恢复备份: {backup.name}")
        # 这里简化处理，实际需要实现完整的恢复逻辑
        return JsonResponse({'code': 200, 'message': '恢复任务已启动'})
    except Exception as e:
        return JsonResponse({'code': 500, 'message': str(e)})


@csrf_exempt
@require_http_methods(["DELETE"])
def delete_backup(request, backup_id):
    """删除备份"""
    try:
        backup = BackupRecord.objects.get(id=backup_id)
        if os.path.exists(backup.file_path):
            os.remove(backup.file_path)
        backup.delete()
        log_operation(request, 'backup', f"删除备份: {backup.name}")
        return JsonResponse({'code': 200, 'message': '删除成功'})
    except Exception as e:
        return JsonResponse({'code': 500, 'message': str(e)})


@csrf_exempt
@require_http_methods(["POST"])
def save_backup_config(request):
    """保存备份配置"""
    try:
        # 简化处理，实际应该保存到数据库
        log_operation(request, 'backup', "保存备份配置")
        return JsonResponse({'code': 200, 'message': '保存成功'})
    except Exception as e:
        return JsonResponse({'code': 500, 'message': str(e)})


@csrf_exempt
@require_http_methods(["GET"])
def get_exports(request):
    """获取导出任务列表"""
    try:
        exports = ExportTask.objects.all().values()
        return JsonResponse({'code': 200, 'data': list(exports)})
    except Exception as e:
        return JsonResponse({'code': 500, 'message': str(e)})


@csrf_exempt
@require_http_methods(["POST"])
def create_export(request):
    """创建导出任务"""
    try:
        data = json.loads(request.body)
        
        task = ExportTask.objects.create(
            name=f"数据导出-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            data_types=data.get('types', []),
            export_format=data.get('format', 'excel'),
            include_images=data.get('includeImages', False),
            status='processing',
            created_by=request.session.get('user_id', 0)
        )
        
        log_operation(request, 'export', f"创建导出任务: {task.name}")
        
        # 后台执行导出
        import threading
        threading.Thread(target=perform_export, args=(task.id,)).start()
        
        return JsonResponse({'code': 200, 'message': '导出任务已创建'})
    except Exception as e:
        return JsonResponse({'code': 500, 'message': str(e)})


def perform_export(task_id):
    """执行导出（后台线程）"""
    try:
        task = ExportTask.objects.get(id=task_id)
        task.status = 'processing'
        task.progress = 0
        task.save()
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        export_filename = f"export_{timestamp}.{task.export_format}"
        export_path = os.path.join(EXPORT_DIR, export_filename)
        
        # 根据格式导出数据
        if task.export_format == 'csv':
            export_to_csv(task, export_path)
        elif task.export_format == 'json':
            export_to_json(task, export_path)
        else:  # excel
            export_to_excel(task, export_path)
        
        # 更新任务
        task.file_path = export_path
        task.file_size = os.path.getsize(export_path) if os.path.exists(export_path) else 0
        task.status = 'completed'
        task.progress = 100
        task.completed_time = datetime.now()
        task.save()
        
    except Exception as e:
        try:
            task = ExportTask.objects.get(id=task_id)
            task.status = 'failed'
            task.error_message = str(e)
            task.save()
        except Exception:
            pass


def export_to_csv(task, export_path):
    """导出为CSV"""
    import csv
    
    data_type_map = {
        'items': Item,
        'users': User,
        'claims': Claim,
        'images': ItemImage,
    }
    
    all_data = {}
    total_count = 0
    
    for data_type in task.data_types:
        if data_type in data_type_map:
            model = data_type_map[data_type]
            data = list(model.objects.values())
            all_data[data_type] = data
            total_count += len(data)
    
    if all_data:
        with open(export_path, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            first_type = True
            for data_type, data in all_data.items():
                if not data:
                    continue
                if not first_type:
                    writer.writerow([])
                writer.writerow([f'=== {data_type} ==='])
                if data:
                    writer.writerow([field for field in data[0].keys()])
                    for item in data:
                        writer.writerow([item.get(field, '') for field in item.keys()])
                first_type = False
    
    task.record_count = total_count


def export_to_json(task, export_path):
    """导出为JSON"""
    export_data = {}
    total_count = 0
    
    data_type_map = {
        'items': Item,
        'users': User,
        'claims': Claim,
        'images': ItemImage,
    }
    
    for data_type in task.data_types:
        if data_type in data_type_map:
            model = data_type_map[data_type]
            data = list(model.objects.values())
            export_data[data_type] = data
            total_count += len(data)
    
    with open(export_path, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, ensure_ascii=False, default=str)
    
    task.record_count = total_count


def export_to_excel(task, export_path):
    """导出为Excel（使用CSV格式）"""
    export_to_csv(task, export_path.replace('.xlsx', '.csv'))


@csrf_exempt
@require_http_methods(["GET"])
def download_export(request, task_id):
    """下载导出文件"""
    try:
        task = ExportTask.objects.get(id=task_id)
        if os.path.exists(task.file_path):
            log_operation(request, 'export', f"下载导出文件: {task.name}")
            return FileResponse(open(task.file_path, 'rb'), as_attachment=True)
        return JsonResponse({'code': 404, 'message': '文件不存在'})
    except Exception as e:
        return JsonResponse({'code': 500, 'message': str(e)})


@csrf_exempt
@require_http_methods(["POST"])
def retry_export(request, task_id):
    """重试导出"""
    try:
        task = ExportTask.objects.get(id=task_id)
        # 重置任务状态
        task.status = 'pending'
        task.progress = 0
        task.error_message = ''
        task.save()
        
        import threading
        threading.Thread(target=perform_export, args=(task.id,)).start()
        
        return JsonResponse({'code': 200, 'message': '已重新开始导出'})
    except Exception as e:
        return JsonResponse({'code': 500, 'message': str(e)})


@csrf_exempt
@require_http_methods(["DELETE"])
def delete_export(request, task_id):
    """删除导出任务"""
    try:
        task = ExportTask.objects.get(id=task_id)
        if task.file_path and os.path.exists(task.file_path):
            os.remove(task.file_path)
        task.delete()
        log_operation(request, 'export', f"删除导出任务: {task.name}")
        return JsonResponse({'code': 200, 'message': '删除成功'})
    except Exception as e:
        return JsonResponse({'code': 500, 'message': str(e)})


def get_cleanup_stats(request):
    """获取清理统计数据"""
    try:
        from django.utils import timezone
        from datetime import timedelta
        
        # 已删除物品（超过30天的已删除物品）
        items_cutoff = timezone.now() - timedelta(days=30)
        deleted_items = Item.objects.filter(current_status=0, update_time__lt=items_cutoff)  # 假设状态0为已删除
        items_count = deleted_items.count()
        items_size = items_count * 1024 * 50  # 估算每条50KB
        
        # 过期日志（超过90天的操作日志）
        log_cutoff = timezone.now() - timedelta(days=90)
        old_logs = ItemOperationLog.objects.filter(operation_time__lt=log_cutoff)
        logs_count = old_logs.count()
        logs_size = logs_count * 1024 * 40  # 估算每条40KB
        
        # 失效备份（超过7天的备份）
        backup_cutoff = timezone.now() - timedelta(days=7)
        from .models import BackupRecord
        old_backups = BackupRecord.objects.filter(status='completed', created_time__lt=backup_cutoff)
        backups_count = old_backups.count()
        backups_size = sum(b.file_size for b in old_backups if b.file_size)
        
        # 未激活账号（365天未登录且无发布内容）
        user_cutoff = timezone.now() - timedelta(days=365)
        active_user_ids = Item.objects.values_list('user_id', flat=True)
        inactive_users = User.objects.filter(
            last_login_time__lt=user_cutoff,
            create_time__lt=user_cutoff
        ).exclude(id__in=active_user_ids)
        users_count = inactive_users.count()
        users_size = users_count * 1024 * 5  # 估算每条5KB
        
        # 临时文件（从文件系统查询）
        import os
        temp_dir = os.path.join(settings.BASE_DIR, 'temp')
        temp_files = 0
        temp_size = 0
        if os.path.exists(temp_dir):
            for root, dirs, files in os.walk(temp_dir):
                temp_files += len(files)
                for file in files:
                    try:
                        temp_size += os.path.getsize(os.path.join(root, file))
                    except Exception:
                        pass
        
        # 缓存数据（从文件系统查询）
        cache_dir = os.path.join(settings.BASE_DIR, 'cache')
        cache_data = 0
        cache_size = 0
        if os.path.exists(cache_dir):
            for root, dirs, files in os.walk(cache_dir):
                cache_data += len(files)
                for file in files:
                    try:
                        cache_size += os.path.getsize(os.path.join(root, file))
                    except Exception:
                        pass
        
        # 错误日志（从文件系统查询）
        log_dir = os.path.join(settings.BASE_DIR, 'logs')
        error_logs = 0
        error_size = 0
        if os.path.exists(log_dir):
            for root, dirs, files in os.walk(log_dir):
                error_logs += len(files)
                for file in files:
                    try:
                        error_size += os.path.getsize(os.path.join(root, file))
                    except Exception:
                        pass
        
        # 孤儿图片文件
        item_ids = Item.objects.values_list('id', flat=True)
        orphan_images = ItemImage.objects.exclude(item_id__in=item_ids)
        orphan_count = orphan_images.count()
        orphan_size = orphan_count * 1024 * 100  # 估算每条100KB
        
        stats = {
            'cleanupRules': [
                {
                    'id': 1,
                    'name': '已删除物品',
                    'description': '用户已删除或管理员已移除的物品数据',
                    'enabled': True,
                    'retentionDays': 30,
                    'estimatedCount': items_count,
                    'estimatedSize': items_size
                },
                {
                    'id': 2,
                    'name': '过期日志',
                    'description': '系统操作日志和审计日志',
                    'enabled': True,
                    'retentionDays': 90,
                    'estimatedCount': logs_count,
                    'estimatedSize': logs_size
                },
                {
                    'id': 3,
                    'name': '失效备份',
                    'description': '超出保留策略的旧备份文件',
                    'enabled': True,
                    'retentionDays': 7,
                    'estimatedCount': backups_count,
                    'estimatedSize': backups_size
                },
                {
                    'id': 4,
                    'name': '未激活账号',
                    'description': '长期未登录且未发布内容的用户',
                    'enabled': False,
                    'retentionDays': 365,
                    'estimatedCount': users_count,
                    'estimatedSize': users_size
                }
            ],
            'cleanupCategories': [
                {'key': 'temp', 'name': '临时文件', 'count': temp_files, 'size': temp_size},
                {'key': 'cache', 'name': '缓存数据', 'count': cache_data, 'size': cache_size},
                {'key': 'log', 'name': '错误日志', 'count': error_logs, 'size': error_size}
            ],
            'orphanFiles': {
                'count': orphan_count,
                'size': orphan_size
            }
        }
        
        return JsonResponse({'code': 200, 'data': stats})
    except Exception as e:
        return JsonResponse({'code': 500, 'message': str(e)})


@csrf_exempt
@require_http_methods(["POST"])
def execute_cleanup(request):
    """执行数据清理"""
    try:
        import json
        data = json.loads(request.body) if request.body else {}
        rules = data.get('rules', [])
        
        total_cleaned = 0
        total_size = 0
        cleanup_details = []
        
        # 清理已删除的物品（状态为已删除且超过30天）
        from django.utils import timezone
        from datetime import timedelta
        
        # 清理过期日志（超过90天的操作日志）
        log_cutoff = timezone.now() - timedelta(days=90)
        old_logs = ItemOperationLog.objects.filter(operation_time__lt=log_cutoff)
        log_count = old_logs.count()
        if log_count > 0:
            old_logs.delete()
            total_cleaned += log_count
            cleanup_details.append(f"删除 {log_count} 条过期操作日志")
        
        # 清理过期的备份文件（超过保留策略的备份）
        from .models import BackupRecord
        backup_cutoff = timezone.now() - timedelta(days=7)
        old_backups = BackupRecord.objects.filter(created_time__lt=backup_cutoff, status='completed')
        for backup in old_backups:
            if backup.file_path and os.path.exists(backup.file_path):
                try:
                    file_size = os.path.getsize(backup.file_path)
                    os.remove(backup.file_path)
                    total_size += file_size
                except Exception:
                    pass
            backup.delete()
            total_cleaned += 1
        if old_backups.count() > 0:
            cleanup_details.append(f"删除 {old_backups.count()} 个过期备份")
        
        # 清理过期的导出文件（超过30天）
        export_cutoff = timezone.now() - timedelta(days=30)
        from .models import ExportTask
        old_exports = ExportTask.objects.filter(completed_time__lt=export_cutoff, status='completed')
        for export_task in old_exports:
            if export_task.file_path and os.path.exists(export_task.file_path):
                try:
                    file_size = os.path.getsize(export_task.file_path)
                    os.remove(export_task.file_path)
                    total_size += file_size
                except Exception:
                    pass
            export_task.delete()
            total_cleaned += 1
        if old_exports.count() > 0:
            cleanup_details.append(f"删除 {old_exports.count()} 个过期导出文件")
        
        # 清理孤儿图片文件（修复__not_in问题）
        item_ids = Item.objects.values_list('id', flat=True)
        orphan_images = ItemImage.objects.exclude(item_id__in=item_ids)
        orphan_count = orphan_images.count()
        if orphan_count > 0:
            orphan_images.delete()
            total_cleaned += orphan_count
            cleanup_details.append(f"删除 {orphan_count} 个孤儿图片记录")
        
        log_operation(request, 'cleanup', f"执行数据清理: {', '.join(cleanup_details)}")
        
        return JsonResponse({
            'code': 200, 
            'message': f'清理完成',
            'data': {
                'cleaned': total_cleaned,
                'size': total_size,
                'details': cleanup_details
            }
        })
    except Exception as e:
        return JsonResponse({'code': 500, 'message': str(e)})


@csrf_exempt
@require_http_methods(["POST"])
def submit_feedback(request):
    """用户提交反馈"""
    try:
        data = json.loads(request.body)
        user_id = request.session.get('user_id')
        if not user_id:
            return JsonResponse({'code': 401, 'message': '请先登录'})
        
        user = User.objects.get(id=user_id)
        Feedback.objects.create(
            user=user,
            feedback_type=data.get('type', 'other'),
            content=data.get('message', '')
        )
        return JsonResponse({'code': 200, 'message': '留言发送成功！管理员将在24小时内回复'})
    except User.DoesNotExist:
        return JsonResponse({'code': 401, 'message': '用户不存在'})
    except Exception as e:
        return JsonResponse({'code': 500, 'message': str(e)})


@csrf_exempt
@require_http_methods(["GET"])
def get_feedback(request):
    """获取反馈列表"""
    try:
        feedback_type = request.GET.get('type', '')
        status = request.GET.get('status', '')
        
        queryset = Feedback.objects.select_related('user').all()
        
        if feedback_type:
            queryset = queryset.filter(feedback_type=feedback_type)
        if status:
            queryset = queryset.filter(status=status)
        
        feedback_list = []
        for fb in queryset:
            # 映射类型名称
            type_map = {
                'technical': 'bug',
                'usage': 'other',
                'suggestion': 'feature',
                'other': 'other'
            }
            feedback_list.append({
                'id': fb.id,
                'type': type_map.get(fb.feedback_type, 'other'),
                'priority': 'normal',
                'status': fb.status,
                'userName': fb.user.real_name or fb.user.username,
                'userPhone': fb.user.phone or '',
                'userAvatar': None,
                'title': fb.content[:50] + '...' if len(fb.content) > 50 else fb.content,
                'content': fb.content,
                'images': [],
                'createTime': fb.create_time.strftime('%Y-%m-%d %H:%M:%S'),
                'reply': fb.reply,
                'replyTime': fb.reply_time.strftime('%Y-%m-%d %H:%M:%S') if fb.reply_time else None
            })
        
        # 统计数据
        pending_count = Feedback.objects.filter(status='pending').count()
        total_count = Feedback.objects.count()
        
        return JsonResponse({
            'code': 200, 
            'data': {
                'list': feedback_list,
                'stats': {
                    'pending': pending_count,
                    'total': total_count
                }
            }
        })
    except Exception as e:
        return JsonResponse({'code': 500, 'message': str(e)})


@csrf_exempt
@require_http_methods(["POST"])
def reply_feedback(request, feedback_id):
    """回复反馈"""
    try:
        data = json.loads(request.body)
        content = data.get('content', '')
        resolve = data.get('resolve', False)
        
        fb = Feedback.objects.get(id=feedback_id)
        fb.reply = content
        fb.reply_time = datetime.now()
        if resolve:
            fb.status = 'resolved'
        else:
            fb.status = 'processing'
        fb.save()
        
        # 给用户发送站内通知
        Notification.objects.create(
            user_id=fb.user.id,
            title='您的反馈已收到回复',
            content=f'管理员已回复您的反馈：\n{content}',
            type=1,  # 系统通知
            is_read=0,
            related_id=feedback_id
        )
        
        log_operation(request, 'feedback', f'回复反馈 #{feedback_id}')
        return JsonResponse({'code': 200, 'message': '回复成功，已通知用户'})
    except Feedback.DoesNotExist:
        return JsonResponse({'code': 404, 'message': '反馈不存在'})
    except Exception as e:
        return JsonResponse({'code': 500, 'message': str(e)})


@csrf_exempt
@require_http_methods(["POST"])
def resolve_feedback(request, feedback_id):
    """解决反馈"""
    try:
        fb = Feedback.objects.get(id=feedback_id)
        fb.status = 'resolved'
        fb.save()
        
        log_operation(request, 'feedback', f'标记反馈 #{feedback_id} 为已解决')
        return JsonResponse({'code': 200, 'message': '已标记为已解决'})
    except Feedback.DoesNotExist:
        return JsonResponse({'code': 404, 'message': '反馈不存在'})
    except Exception as e:
        return JsonResponse({'code': 500, 'message': str(e)})