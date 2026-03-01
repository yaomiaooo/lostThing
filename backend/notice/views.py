# backend/notice/views.py

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST
from django.core.paginator import Paginator
from django.db import models

from .models import Notice, Notification
from django.views.decorators.http import require_http_methods

# ==================== 原有接口保持不变 ====================

@require_GET
def get_announcements(request):
    """
    获取系统通知与公告列表（登录后显示）
    URL: GET /api/announcements
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


# ==================== 管理员公告管理接口（修改后） ====================

def check_admin_permission(request):
    """检查是否为管理员"""
    user_id = request.session.get('user_id')
    role = request.session.get('role')
    
    if not user_id:
        return False, JsonResponse({"code": 401, "msg": "未登录"})
    
    if role not in [3, 4]:
        return False, JsonResponse({"code": 403, "msg": "无权限操作"})
    
    return True, None


@require_GET
def get_all_notices(request):
    """
    获取所有公告列表（管理员用）- 原有接口保持不变
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
    
    # 5. 组装数据（移除 type 和 need_confirm）
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
    创建公告（管理员）- 原有接口保持不变
    URL: POST /api/announcements/create
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


# ==================== 新增：管理员公告管理接口（适配无 type/need_confirm 字段）====================

@require_GET
def get_admin_announcement_list(request):
    """
    获取公告管理列表（管理员）- 修改后版本（移除 type 筛选）
    URL: GET /api/announcements/admin/list?page=1&size=10&status=1&priority=1&keyword=维护
    """
    has_perm, error_response = check_admin_permission(request)
    if not has_perm:
        return error_response
    
    # 获取参数（移除 type 筛选）
    page = int(request.GET.get('page', 1))
    size = int(request.GET.get('size', 10))
    status = request.GET.get('status')
    priority = request.GET.get('priority')
    keyword = request.GET.get('keyword')
    
    # 基础查询
    queryset = Notice.objects.all().order_by('-create_time')
    
    # 筛选（移除 type 筛选）
    if status:
        queryset = queryset.filter(status=status)
    if priority:
        queryset = queryset.filter(priority=priority)
    if keyword:
        queryset = queryset.filter(
            models.Q(title__icontains=keyword) |
            models.Q(content__icontains=keyword)
        )
    
    # 分页
    paginator = Paginator(queryset, size)
    page_obj = paginator.get_page(page)
    
    # 组装数据（移除 type 和 need_confirm）
    data_list = []
    for notice in page_obj:
        # 查询创建人信息
        from user.models import User
        creator = User.objects.filter(id=notice.create_user_id).first()
        
        data_list.append({
            "noticeId": notice.id,
            "title": notice.title,
            "content": notice.content,
            "priority": notice.priority,
            "priorityName": {1: "高", 2: "中", 3: "低"}.get(notice.priority, "中"),
            "status": notice.status,
            "statusName": "启用" if notice.status == 1 else "禁用",
            "startTime": notice.start_time.strftime('%Y-%m-%d %H:%M:%S') if notice.start_time else None,
            "endTime": notice.end_time.strftime('%Y-%m-%d %H:%M:%S') if notice.end_time else None,
            "createTime": notice.create_time.strftime('%Y-%m-%d %H:%M:%S') if notice.create_time else None,
            "createUserId": notice.create_user_id,
            "createUserName": creator.real_name if creator else "未知"
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
def publish_announcement(request):
    """
    发布全局公告（管理员）- 修改后版本（移除 type 和 need_confirm）
    URL: POST /api/announcements/admin
    Body: {
        "title": "系统维护通知",
        "content": "系统将于今晚进行维护...",
        "priority": 1,  // 1-高 2-中 3-低
        "startTime": "2026-03-01 00:00:00",
        "endTime": "2026-03-02 00:00:00"
    }
    """
    has_perm, error_response = check_admin_permission(request)
    if not has_perm:
        return error_response
    
    try:
        body = json.loads(request.body.decode('utf-8'))
        title = body.get('title')
        content = body.get('content')
        priority = body.get('priority', 2)
        start_time_str = body.get('startTime')
        end_time_str = body.get('endTime')
        
        # 参数校验（简化，移除 type 和 need_confirm）
        if not all([title, content, start_time_str, end_time_str]):
            return JsonResponse({"code": 400, "msg": "标题、内容、开始时间、结束时间不能为空"})
        
        # 解析时间
        try:
            from datetime import datetime
            start_time = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S')
            end_time = datetime.strptime(end_time_str, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return JsonResponse({"code": 400, "msg": "时间格式错误，应为 YYYY-MM-DD HH:MM:SS"})
        
        user_id = request.session.get('user_id')
        
        # 创建公告（简化，只保留原有字段）
        notice = Notice.objects.create(
            title=title,
            content=content,
            priority=priority,
            start_time=start_time,
            end_time=end_time,
            status=1,  # 启用
            create_user_id=user_id
        )
        
        return JsonResponse({
            "code": 200,
            "msg": "发布成功",
            "data": {
                "noticeId": notice.id,
                "title": notice.title,
                "createTime": notice.create_time.strftime('%Y-%m-%d %H:%M:%S') if notice.create_time else None
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({"code": 400, "msg": "请求数据不是合法的 JSON"})
    except Exception as e:
        return JsonResponse({"code": 500, "msg": f"发布失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["PUT"])
def update_announcement(request, announcement_id):
    """
    修改公告 - 修改后版本（移除 type 和 need_confirm）
    URL: PUT /api/announcements/admin/{announcement_id}
    Body: {
        "title": "修改后的标题",
        "content": "修改后的内容",
        "priority": 2,
        "status": 1,
        "startTime": "2026-03-01 00:00:00",
        "endTime": "2026-03-02 00:00:00"
    }
    """
    has_perm, error_response = check_admin_permission(request)
    if not has_perm:
        return error_response
    
    try:
        notice = Notice.objects.get(id=announcement_id)
    except Notice.DoesNotExist:
        return JsonResponse({"code": 404, "msg": "公告不存在"})
    
    try:
        body = json.loads(request.body.decode('utf-8'))
        
        # 更新字段（移除 type 和 need_confirm）
        if 'title' in body:
            notice.title = body['title']
        if 'content' in body:
            notice.content = body['content']
        if 'priority' in body:
            notice.priority = body['priority']
        if 'status' in body:
            notice.status = body['status']
        
        # 时间字段
        if 'startTime' in body:
            try:
                from datetime import datetime
                notice.start_time = datetime.strptime(body['startTime'], '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return JsonResponse({"code": 400, "msg": "开始时间格式错误"})
        
        if 'endTime' in body:
            try:
                from datetime import datetime
                notice.end_time = datetime.strptime(body['endTime'], '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return JsonResponse({"code": 400, "msg": "结束时间格式错误"})
        
        notice.save()
        
        return JsonResponse({
            "code": 200,
            "msg": "修改成功",
            "data": {
                "noticeId": notice.id,
                "title": notice.title,
                "updateTime": timezone.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({"code": 400, "msg": "请求数据不是合法的 JSON"})
    except Exception as e:
        return JsonResponse({"code": 500, "msg": f"修改失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["DELETE"])
def delete_announcement(request, announcement_id):
    """
    删除公告 - 保持不变
    URL: DELETE /api/announcements/admin/{announcement_id}/delete
    """
    has_perm, error_response = check_admin_permission(request)
    if not has_perm:
        return error_response
    
    try:
        notice = Notice.objects.get(id=announcement_id)
    except Notice.DoesNotExist:
        return JsonResponse({"code": 404, "msg": "公告不存在"})
    
    try:
        notice.delete()
        return JsonResponse({
            "code": 200,
            "msg": "删除成功",
            "data": {"noticeId": announcement_id}
        })
    except Exception as e:
        return JsonResponse({"code": 500, "msg": f"删除失败: {str(e)}"})