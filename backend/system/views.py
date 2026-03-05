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
from .models import BackupRecord, ExportTask, OperationLog
from items.models import Item, ItemImage, ItemStatusHistory, Category, Location, Claim, OperationLog as ItemOperationLog
from user.models import User
from chat.models import Conversation, Message
from notice.models import Notice

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


@csrf_exempt
@require_http_methods(["POST"])
def execute_cleanup(request):
    """执行数据清理"""
    try:
        log_operation(request, 'cleanup', "执行数据清理")
        return JsonResponse({'code': 200, 'message': '清理任务已启动'})
    except Exception as e:
        return JsonResponse({'code': 500, 'message': str(e)})


@csrf_exempt
@require_http_methods(["GET"])
def get_feedback(request):
    """获取反馈列表（临时实现）"""
    return JsonResponse({'code': 200, 'data': {'list': []}})


@csrf_exempt
@require_http_methods(["POST"])
def reply_feedback(request, feedback_id):
    """回复反馈"""
    return JsonResponse({'code': 200, 'message': '回复成功'})


@csrf_exempt
@require_http_methods(["POST"])
def resolve_feedback(request, feedback_id):
    """解决反馈"""
    return JsonResponse({'code': 200, 'message': '已标记为已解决'})