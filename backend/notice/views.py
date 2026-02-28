# backend/notice/views.py

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST
from django.core.paginator import Paginator

from .models import Notice, Notification


@require_GET
def get_announcements(request):
    """
    获取系统通知与公告列表（登录后显示）
    URL: GET /api/announcements
    返回未读公告和当前有效的公告
    """
    
    # 1. 登录校验
    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse({
            "code": 401,
            "msg": "未登录"
        })
    
    # 2. 获取当前时间
    now = timezone.now()
    
    # 3. 查询当前有效的公告（在有效期内且状态为启用）
    announcements = Notice.objects.filter(
        status=1,  # 启用状态
        start_time__lte=now,
        end_time__gte=now
    ).order_by('-priority', '-create_time')
    
    # 4. 查询用户未读的通知
    unread_notifications = Notification.objects.filter(
        user_id=user_id,
        is_read=0
    ).order_by('-create_time')
    
    # 5. 组装公告数据
    announcement_list = []
    for notice in announcements:
        announcement_list.append({
            "noticeId": notice.id,
            "title": notice.title,
            "content": notice.content,
            "priority": notice.priority,  # 1-高, 2-中, 3-低
            "startTime": notice.start_time.strftime('%Y-%m-%d %H:%M:%S'),
            "endTime": notice.end_time.strftime('%Y-%m-%d %H:%M:%S'),
            "createTime": notice.create_time.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    # 6. 组装未读通知数据
    notification_list = []
    for notif in unread_notifications:
        notification_list.append({
            "notificationId": notif.id,
            "title": notif.title,
            "content": notif.content,
            "type": notif.type,
            "relatedId": notif.related_id,
            "createTime": notif.create_time.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    # 7. 检查是否有需要强制确认的公告（高优先级）
    need_confirm = any(a['priority'] == 1 for a in announcement_list)
    
    return JsonResponse({
        "code": 200,
        "msg": "success",
        "data": {
            "announcements": announcement_list,
            "unreadNotifications": notification_list,
            "totalAnnouncements": len(announcement_list),
            "totalUnreadNotifications": len(notification_list),
            "needConfirm": need_confirm  # 是否需要强制确认后才能进入主界面
        }
    })


@csrf_exempt
@require_POST
def confirm_announcement_read(request):
    """
    确认已读公告/通知
    URL: POST /api/announcements/read
    Body: {
        "noticeIds": [1, 2],      // 已读公告ID列表
        "notificationIds": [3, 4]  // 已读通知ID列表
    }
    """
    
    # 1. 登录校验
    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse({
            "code": 401,
            "msg": "未登录"
        })
    
    # 2. 解析参数
    try:
        body = json.loads(request.body.decode('utf-8'))
        notice_ids = body.get('noticeIds', [])
        notification_ids = body.get('notificationIds', [])
    except json.JSONDecodeError:
        return JsonResponse({
            "code": 400,
            "msg": "请求数据不是合法的 JSON"
        })
    
    # 3. 标记通知为已读（实际项目中可能需要创建已读记录表）
    # 简化处理：将用户的通知标记为已读
    updated_count = 0
    if notification_ids:
        updated_count = Notification.objects.filter(
            id__in=notification_ids,
            user_id=user_id
        ).update(
            is_read=1,
            read_time=timezone.now()
        )
    
    # 4. 记录公告阅读（可选：创建阅读记录）
    # 这里简化处理，仅返回成功
    
    return JsonResponse({
        "code": 200,
        "msg": "确认成功",
        "data": {
            "updatedNotifications": updated_count,
            "confirmedAt": timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    })


# ==================== 管理员公告管理接口（可选） ====================

@require_GET
def get_all_notices(request):
    """
    获取所有公告列表（管理员用）
    URL: GET /api/announcements/all?page=1&size=10
    """
    
    # 1. 登录和权限校验
    user_id = request.session.get('user_id')
    role = request.session.get('role')
    
    if not user_id:
        return JsonResponse({
            "code": 401,
            "msg": "未登录"
        })
    
    if role not in [3, 4]:  # 只允许管理员
        return JsonResponse({
            "code": 403,
            "msg": "无权限"
        })
    
    # 2. 获取参数
    page = int(request.GET.get('page', 1))
    size = int(request.GET.get('size', 10))
    status = request.GET.get('status')
    
    # 3. 查询
    queryset = Notice.objects.all().order_by('-create_time')
    
    if status:
        queryset = queryset.filter(status=status)
    
    # 4. 分页
    paginator = Paginator(queryset, size)
    page_obj = paginator.get_page(page)
    
    # 5. 组装数据
    data_list = []
    for notice in page_obj:
        data_list.append({
            "noticeId": notice.id,
            "title": notice.title,
            "content": notice.content,
            "priority": notice.priority,
            "status": notice.status,
            "startTime": notice.start_time.strftime('%Y-%m-%d %H:%M:%S') if notice.start_time else None,
            "endTime": notice.end_time.strftime('%Y-%m-%d %H:%M:%S') if notice.end_time else None,
            "createTime": notice.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            "createUserId": notice.create_user_id
        })
    
    return JsonResponse({
        "code": 200,
        "msg": "success",
        "data": {
            "list": data_list,
            "page": page_obj.number,
            "size": size,
            "total": paginator.count
        }
    })


@csrf_exempt
@require_POST
def create_notice(request):
    """
    创建公告（管理员）
    URL: POST /api/announcements
    Body: {
        "title": "系统维护通知",
        "content": "系统将于今晚进行维护...",
        "priority": 1,
        "startTime": "2026-02-28 00:00:00",
        "endTime": "2026-03-01 00:00:00"
    }
    """
    
    # 1. 登录和权限校验
    user_id = request.session.get('user_id')
    role = request.session.get('role')
    
    if not user_id:
        return JsonResponse({
            "code": 401,
            "msg": "未登录"
        })
    
    if role not in [3, 4]:
        return JsonResponse({
            "code": 403,
            "msg": "无权限"
        })
    
    # 2. 解析参数
    try:
        body = json.loads(request.body.decode('utf-8'))
        title = body.get('title')
        content = body.get('content')
        priority = body.get('priority', 2)
        start_time_str = body.get('startTime')
        end_time_str = body.get('endTime')
    except json.JSONDecodeError:
        return JsonResponse({
            "code": 400,
            "msg": "请求数据不是合法的 JSON"
        })
    
    # 3. 参数校验
    if not all([title, content, start_time_str, end_time_str]):
        return JsonResponse({
            "code": 400,
            "msg": "标题、内容、开始时间、结束时间不能为空"
        })
    
    # 4. 解析时间
    try:
        from datetime import datetime
        start_time = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S')
        end_time = datetime.strptime(end_time_str, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return JsonResponse({
            "code": 400,
            "msg": "时间格式错误，应为 YYYY-MM-DD HH:MM:SS"
        })
    
    # 5. 创建公告
    try:
        notice = Notice.objects.create(
            title=title,
            content=content,
            priority=priority,
            start_time=start_time,
            end_time=end_time,
            status=1,  # 启用
            create_user_id=user_id
        )
    except Exception as e:
        return JsonResponse({
            "code": 500,
            "msg": "创建失败",
            "error": str(e)
        })
    
    return JsonResponse({
        "code": 200,
        "msg": "创建成功",
        "data": {
            "noticeId": notice.id
        }
    })