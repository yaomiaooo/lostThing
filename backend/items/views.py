from django.shortcuts import render

# backend/items/views.py

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from django.views.decorators.http import require_GET
from django.core.paginator import Paginator

from django.views.decorators.http import require_POST

from .models import Item, Location, Claim, Category,ItemStatusHistory,ItemImage
from user.models import User
from notice.models import Notification

from django.db import transaction
from django.utils.dateparse import parse_datetime

from datetime import datetime

# 在文件顶部导入部分添加
from django.views.decorators.http import require_http_methods
from django.db import models

# 物品状态常量
ITEM_STATUS = {
    1: '待审核',
    2: '已通过',
    3: '已匹配',
    4: '已认领',
    5: '已驳回',
    6: '已取消',
    7: '已归档',
    8: '无效',
}

@csrf_exempt
def add_item(request):
    """
    6.4.1 发布失物 / 招领信息
    URL: POST /api/item
    """

    # 1. 只允许 POST 请求
    if request.method != 'POST':
        return JsonResponse({
            'code': 405,
            'msg': '请求方法不允许'
        })

    # 2. 获取当前登录用户
    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse({
            'code': 401,
            'msg': '未登录，请先登录'
        })

    # 3. 解析 JSON 数据
    try:
        body = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({
            'code': 400,
            'msg': '请求数据不是合法的 JSON'
        })

    # 4. 获取参数（与数据库字段一一对应）
    item_category = body.get('itemCategory')       # 1=失物，2=招领
    item_type = body.get('itemType')               # category.id
    name = body.get('name')
    location_id = body.get('locationId')
    location_detail = body.get('locationDetail', '')
    pickup_location = body.get('pickupLocation', '')   # 新增：领取地点
    happen_time = body.get('happenTime')
    feature = body.get('feature', '')
    reward_amount = body.get('rewardAmount', 0)
    reward_desc = body.get('rewardDesc', '')
    contact_name = body.get('contactName')
    contact_phone = body.get('contactPhone')

    # 5. 必填参数校验
    if not all([
        item_category,
        item_type,
        name,
        location_id,
        happen_time,
        contact_name,
        contact_phone
    ]):
        return JsonResponse({
            'code': 400,
            'msg': '缺少必要参数'
        })

    # 6. 校验 item_category 合法性
    if item_category not in [1, 2]:
        return JsonResponse({
            'code': 400,
            'msg': 'itemCategory 参数非法'
        })

    # 7. 解析时间（前端一般传字符串）
    try:
        # 示例格式：2026-02-01 14:30:00
        happen_time = datetime.strptime(happen_time, '%Y-%m-%d %H:%M:%S')
    except Exception:
        return JsonResponse({
            'code': 400,
            'msg': 'happenTime 时间格式错误，应为 YYYY-MM-DD HH:MM:SS'
        })

    # 8. 业务规则
    # 招领信息不能有悬赏
    if item_category == 2:
        reward_amount = 0
        reward_desc = ''

    # 9. 创建 Item 对象
    try:
        item = Item.objects.create(
            user_id=user_id,
            item_type=item_type,
            item_category=item_category,
            name=name,
            location_id=location_id,
            location_detail=location_detail,
            pickup_location=pickup_location,   # 新增字段
            happen_time=happen_time,
            feature=feature,
            reward_amount=reward_amount,
            reward_desc=reward_desc,
            contact_name=contact_name,
            contact_phone=contact_phone,
            current_status=1,                  # 1 = 待审核
            create_time=timezone.now(),
            update_time=timezone.now()
        )
    except Exception as e:
        return JsonResponse({
            'code': 500,
            'msg': '保存失败',
            'error': str(e)
        })

    # 10. 返回结果
    return JsonResponse({
        'code': 200,
        'msg': '发布成功',
        'data': {
            'itemId': item.id
        }
    })





@require_GET
def get_item_list(request):
    """
    6.4.2 物品列表查询
    URL: GET /api/item/list
    """

    # ========= 1. 获取参数 =========
    item_category = request.GET.get('itemCategory')
    item_type = request.GET.get('itemType')
    location_id = request.GET.get('locationId')
    status = request.GET.get('status')  # 关键参数

    page = int(request.GET.get('page', 1))
    size = int(request.GET.get('size', 10))

    # ========= 2. 基础查询 =========
    queryset = Item.objects.all().order_by('-create_time')

    # ========= 3. 状态过滤逻辑 =========
    if status:
        if status != 'all':
            queryset = queryset.filter(current_status=status)
    else:
        # 普通用户默认：只看审核通过
        queryset = queryset.filter(current_status=2)

    # ========= 4. 其他筛选 =========
    if item_category:
        queryset = queryset.filter(item_category=item_category)

    if item_type:
        queryset = queryset.filter(item_type=item_type)

    if location_id:
        # 如果location_id是单个数字（1-4），表示按校区筛选
        # 1xxxx = 朝晖校区, 2xxxx = 屏峰校区, 3xxxx = 莫干山校区, 4xxxx = 西湖校区
        if location_id in ['1', '2', '3', '4']:
            # 使用字符串前缀匹配
            from django.db.models import CharField
            from django.db.models.functions import Cast
            queryset = queryset.annotate(
                location_id_str=Cast('location_id', CharField())
            ).filter(location_id_str__startswith=location_id)
        else:
            # 否则按精确的location_id筛选
            queryset = queryset.filter(location_id=location_id)

    # ========= 5. 分页 =========
    paginator = Paginator(queryset, size)
    page_obj = paginator.get_page(page)

    # ========= 6. 返回数据 =========
    data_list = []

    for item in page_obj:
        location_name = ""
        if item.location_id:
            location = Location.objects.filter(id=item.location_id).first()
            if location:
                location_name = location.name
       # 查询该物品的第一张图片
        first_image = ItemImage.objects.filter(
            item_id=item.id
        ).order_by("sort").first()

        first_image_url = None
        if first_image:
            first_image_url = f"/api/item/image/{first_image.id}"

        data_list.append({
            "itemId": item.id,
            "name": item.name,
            "itemCategory": item.item_category,
            "itemType": item.item_type,
            "locationId": item.location_id,
            "locationName": location_name,
            "happenTime": item.happen_time.strftime('%Y-%m-%d %H:%M:%S'),
            "rewardAmount": float(item.reward_amount),
            "currentStatus": item.current_status,  
            "createTime": item.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            "firstImageUrl": first_image_url   # 新增：物品的第一张图片
        })

    return JsonResponse({
        "code": 200,
        "msg": "ok",
        "data": {
            "list": data_list,
            "page": page_obj.number,
            "size": size,
            "total": paginator.count
        }
    })

def get_item_detail(request):
    """
    6.4.3 查看物品详情
    GET /api/item/detail?itemId=1
    """

    item_id = request.GET.get("itemId")
    if not item_id:
        return JsonResponse({
            "code": 400,
            "msg": "缺少 itemId 参数"
        })

    # 1. 查询物品
    try:
        item = Item.objects.get(id=item_id)
    except Item.DoesNotExist:
        return JsonResponse({
            "code": 404,
            "msg": "物品不存在"
        })

    # 2. 查询分类
    category = Category.objects.filter(id=item.item_type).first()

    # 3. 查询地点
    location = Location.objects.filter(id=item.location_id).first()

    # 4. 查询图片（不返回二进制）
    images = ItemImage.objects.filter(
        item_id=item.id
    ).order_by("sort")

    image_list = []
    for img in images:
        image_list.append({
            "id": img.id,
            "url": f"/api/item/image/{img.id}",
            "type": img.image_type,
            "sort": img.sort
        })

    # 5. 查询状态历史
    histories = ItemStatusHistory.objects.filter(
        item_id=item.id
    ).order_by("operate_time")

    history_list = []
    for h in histories:
        history_list.append({
            "oldStatus": h.old_status,
            "newStatus": h.new_status,
            "operatorId": h.operator_id,
            "operatorType": h.operator_type,
            "reason": h.operate_reason,
            "operateTime": h.operate_time.strftime("%Y-%m-%d %H:%M:%S")
        })

    # 6. 组装返回数据
    data = {
        "item": {
            "id": item.id,
            "userId": item.user_id,
            "itemType": item.item_type,
            "itemCategory": item.item_category,
            "name": item.name,
            "locationId": item.location_id,
            "locationDetail": item.location_detail,
            "pickupLocation": item.pickup_location,
            "happenTime": item.happen_time.strftime("%Y-%m-%d %H:%M:%S"),
            "feature": item.feature,
            "rewardAmount": float(item.reward_amount),
            "rewardDesc": item.reward_desc,
            "contactName": item.contact_name,
            "contactPhone": item.contact_phone,
            "currentStatus": item.current_status,
            "rejectReason": item.reject_reason,
            "archiveDesc": item.archive_desc,
            "auditUserId": item.audit_user_id,
            "auditTime": item.audit_time.strftime("%Y-%m-%d %H:%M:%S") if item.audit_time else None,
            "createTime": item.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "updateTime": item.update_time.strftime("%Y-%m-%d %H:%M:%S")
        },
        "category": {
            "id": category.id,
            "name": category.name
        } if category else None,
        "location": {
            "id": location.id,
            "name": location.name
        } if location else None,
        "images": image_list,
        "statusHistory": history_list
    }

    return JsonResponse({
        "code": 200,
        "msg": "查询成功",
        "data": data
    })

@csrf_exempt
@require_POST
def audit_item(request):
    """
    6.4.4 管理员审核物品
    URL: POST /api/item/audit
    """

    # ===== 0. 登录校验 =====
    user_id = request.session.get('user_id')
    role = request.session.get('role')

    if not user_id:
        return JsonResponse({
            "code": 401,
            "msg": "未登录"
        })

    # 只允许管理员角色
    # 3 = 失物招领管理员，4 = 系统管理员
    if role not in [3, 4]:
        return JsonResponse({
            "code": 403,
            "msg": "无权限操作"
        })

    try:
        # 1. 解析 JSON
        body = json.loads(request.body.decode("utf-8"))

        item_id = body.get("itemId")
        status = body.get("status")
        reject_reason = body.get("rejectReason", "")

        # 2. 参数校验
        if not item_id or not status:
            return JsonResponse({
                "code": 400,
                "msg": "参数缺失"
            })

        # 3. 查询物品
        try:
            item = Item.objects.get(id=item_id)
        except Item.DoesNotExist:
            return JsonResponse({
                "code": 404,
                "msg": "物品不存在"
            })

        # 4. 状态校验
        if status not in [2, 5]:
            return JsonResponse({
                "code": 400,
                "msg": "非法的审核状态"
            })

        # 5. 记录旧状态
        old_status = item.current_status

        # 6. 更新审核信息
        item.current_status = status
        item.audit_time = timezone.now()
        item.audit_user_id = user_id   # 来自 session

        # 7. 驳回必须写原因
        if status == 5:
            if not reject_reason:
                return JsonResponse({
                    "code": 400,
                    "msg": "驳回时必须填写驳回原因"
                })
            item.reject_reason = reject_reason

        item.save()

        # 8. 记录状态历史
        ItemStatusHistory.objects.create(
            item_id=item.id,
            old_status=old_status,
            new_status=status,
            operator_id=user_id,
            operator_type=2,  # 2=管理员
            operate_reason=reject_reason if status == 5 else "审核通过",
            operate_time=timezone.now()
        )

        # 9. 发送通知给发布者
        if status == 2:
            # 审核通过通知
            Notification.objects.create(
                user_id=item.user_id,
                title="物品审核已通过",
                content=f"您发布的物品【{item.name}】已通过审核，现在可以正常展示了。",
                type=1,  # 物品相关
                related_id=item.id
            )
        elif status == 5:
            # 审核驳回通知
            Notification.objects.create(
                user_id=item.user_id,
                title="物品审核已驳回",
                content=f"您发布的物品【{item.name}】未通过审核。驳回原因：{reject_reason}",
                type=1,  # 物品相关
                related_id=item.id
            )

        return JsonResponse({
            "code": 200,
            "msg": "审核成功"
        })

    except Exception as e:
        return JsonResponse({
            "code": 500,
            "msg": "服务器错误",
            "error": str(e)
        })


@csrf_exempt
def add_claim(request):
    """
    6.4.5 认领物品
    URL: POST /api/claim
    """

    # ===== 0. 登录校验 =====
    user_id = request.session.get("user_id")

    if not user_id:
        return JsonResponse({
            "code": 401,
            "msg": "未登录"
        })

    # 1. 只允许 POST
    if request.method != 'POST':
        return JsonResponse({
            "code": 405,
            "msg": "请求方式错误"
        })

    try:
        # 2. 解析 JSON
        data = json.loads(request.body.decode('utf-8'))
        item_id = data.get('itemId')
        proof_feature = data.get('proofFeature')

        # 3. 参数校验
        if not item_id or not proof_feature:
            return JsonResponse({
                "code": 400,
                "msg": "参数不能为空"
            })

        # 4. 判断物品是否存在
        try:
            item = Item.objects.get(id=item_id)
        except Item.DoesNotExist:
            return JsonResponse({
                "code": 404,
                "msg": "物品不存在"
            })

        # 只允许“审核通过”的物品被认领
        if item.current_status != 2:
            return JsonResponse({
                "code": 400,
                "msg": "该物品当前不可认领"
            })

        # 5. 创建认领申请
        Claim.objects.create(
            item_id=item_id,
            claim_user_id=user_id,     # 当前登录用户
            proof_feature=proof_feature,
            status=0                   # 0 = 待审核
        )

        return JsonResponse({
            "code": 200,
            "msg": "认领申请提交成功"
        })

    except Exception as e:
        return JsonResponse({
            "code": 500,
            "msg": "服务器错误",
            "error": str(e)
        })

@csrf_exempt
def upload_item_image(request):
    """
    6.4.6 上传物品图片（图片存 MySQL）
    URL: /api/item/image/upload
    """

    if request.method != 'POST':
        return JsonResponse({'code': 405, 'msg': '请求方法不允许'})

    # 登录校验
    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse({'code': 401, 'msg': '未登录'})

    # 参数
    item_id = request.POST.get('itemId')
    image_type = request.POST.get('imageType')
    sort = request.POST.get('sort', 1)
    file = request.FILES.get('file')

    if not all([item_id, image_type, file]):
        return JsonResponse({'code': 400, 'msg': '缺少必要参数'})

    # 校验物品是否存在
    if not Item.objects.filter(id=item_id).exists():
        return JsonResponse({'code': 404, 'msg': '物品不存在'})

    try:
        # 读取图片二进制
        image_bytes = file.read()

        item_image = ItemImage.objects.create(
            item_id=item_id,
            image_data=image_bytes,
            image_url=file.name,   # 保存原始文件名（可选）
            image_type=int(image_type),
            sort=int(sort)
        )

    except Exception as e:
        return JsonResponse({
            'code': 500,
            'msg': '图片上传失败',
            'error': str(e)
        })

    return JsonResponse({
        'code': 200,
        'msg': '图片上传成功',
        'data': {
            'imageId': item_image.id
        }
    })





def build_category_tree(data_list, parent_id=0):
    """
    递归构建分类树
    """
    tree = []
    for item in data_list:
        if item["parent_id"] == parent_id:
            children = build_category_tree(data_list, item["id"])
            if children:
                item["children"] = children
            tree.append(item)
    return tree


def get_category_tree(request):
    """
    获取分类树
    GET /api/item/category/tree
    """
    if request.method != "GET":
        return JsonResponse({
            "code": 405,
            "msg": "请求方式不允许"
        })

    # 1. 查询所有启用分类
    qs = Category.objects.filter(status=1).order_by("-sort").values(
        "id",
        "name",
        "parent_id"
    )

    category_list = list(qs)

    # 2. 构建树
    tree = build_category_tree(category_list, parent_id=0)

    return JsonResponse({
        "code": 200,
        "msg": "success",
        "data": tree
    })


def build_location_tree(data_list, parent_id=0):
    """
    递归构建地点树
    """
    tree = []
    for item in data_list:
        if item["parent_id"] == parent_id:
            children = build_location_tree(data_list, item["id"])
            if children:
                item["children"] = children
            tree.append(item)
    return tree


def get_location_tree(request):
    """
    获取地点树
    GET /api/item/location/tree
    """
    if request.method != "GET":
        return JsonResponse({
            "code": 405,
            "msg": "请求方式不允许"
        })

    # 1. 查询所有启用地点
    qs = Location.objects.filter(status=1).order_by("-sort").values(
        "id",
        "name",
        "parent_id"
    )

    location_list = list(qs)

    # 2. 构建树
    tree = build_location_tree(location_list, parent_id=0)

    return JsonResponse({
        "code": 200,
        "msg": "success",
        "data": tree
    })

from django.http import HttpResponse

def get_item_image(request, image_id):
    """
    获取物品图片
    GET /api/item/image/{image_id}
    """
    if request.method != "GET":
        return JsonResponse({
            "code": 405,
            "msg": "请求方式不允许"
        })

    try:
        img = ItemImage.objects.get(id=image_id)
    except ItemImage.DoesNotExist:
        return HttpResponse(status=404)

    return HttpResponse(
        img.image_data,
        content_type="image/jpeg"
    )

@require_GET
def get_my_posts(request):
    """
    获取当前用户的发布记录
    URL: GET /api/item/my-posts
    """
    
    # 1. 登录校验
    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse({
            "code": 401,
            "msg": "未登录"
        })
    
    # 2. 获取参数
    status_filter = request.GET.get('status')
    page = int(request.GET.get('page', 1))
    size = int(request.GET.get('size', 10))
    
    # 3. 查询当前用户的所有物品，只查询状态1-6（排除已归档和无效）
    queryset = Item.objects.filter(
        user_id=user_id,
        current_status__range=[1, 6]  # 只包含1-6
    ).order_by('-create_time')
    
    # 4. 状态筛选
    if status_filter:
        if status_filter != 'all':
            # 支持多个状态筛选，如 status=1,2,3
            status_list = []
            for s in status_filter.split(','):
                s = s.strip()
                if s.isdigit():
                    status_list.append(int(s))
            
            # 确保状态在1-6范围内
            status_list = [s for s in status_list if 1 <= s <= 6]
            if status_list:
                queryset = queryset.filter(current_status__in=status_list)
    
    # 5. 分页
    paginator = Paginator(queryset, size)
    page_obj = paginator.get_page(page)
    
    # 6. 构建返回数据
    data_list = []
    for item in page_obj:
        # 获取地点名称 - 使用原始的查询方式
        location_name = ""
        if item.location_id:
            try:
                location = Location.objects.get(id=item.location_id)
                location_name = location.name
            except Location.DoesNotExist:
                location_name = ""
        
        # 获取分类名称
        category_name = ""
        if item.item_type:
            try:
                category = Category.objects.get(id=item.item_type)
                category_name = category.name
            except Category.DoesNotExist:
                category_name = ""
        
        # 获取第一张图片
        first_image = ItemImage.objects.filter(
            item_id=item.id
        ).order_by("sort").first()
        
        first_image_url = None
        if first_image:
            first_image_url = f"/api/item/image/{first_image.id}"
        
        data_list.append({
            "itemId": item.id,
            "userId": item.user_id,
            "name": item.name,
            "itemCategory": item.item_category,
            "itemType": item.item_type,
            "itemTypeName": category_name,
            "locationId": item.location_id,
            "locationName": location_name,
            "locationDetail": item.location_detail,
            "pickupLocation": item.pickup_location,
            "happenTime": item.happen_time.strftime('%Y-%m-%d %H:%M:%S'),
            "feature": item.feature,
            "rewardAmount": float(item.reward_amount),
            "rewardDesc": item.reward_desc,
            "contactName": item.contact_name,
            "contactPhone": item.contact_phone,
            "currentStatus": item.current_status,
            "rejectReason": item.reject_reason,
            "createTime": item.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            "updateTime": item.update_time.strftime('%Y-%m-%d %H:%M:%S'),
            "firstImageUrl": first_image_url
        })
    
    # 7. 统计各类状态数量（只统计1-6）
    total = queryset.count()
    pending = queryset.filter(current_status=1).count()
    approved = queryset.filter(current_status=2).count()
    matched = queryset.filter(current_status=3).count()
    claimed = queryset.filter(current_status=4).count()
    rejected = queryset.filter(current_status=5).count()
    canceled = queryset.filter(current_status=6).count()
    
    return JsonResponse({
        "code": 200,
        "msg": "success",
        "data": {
            "list": data_list,
            "page": page_obj.number,
            "size": size,
            "total": paginator.count,
            "statistics": {
                "total": total,
                "pending": pending,
                "approved": approved,
                "matched": matched,
                "claimed": claimed,
                "rejected": rejected,
                "canceled": canceled
            }
        }
    })

@csrf_exempt
def update_item(request, item_id):
    """
    修改物品信息
    URL: PUT /api/item/{item_id}
    说明：用户只能修改自己发布的物品，且只能修改待审核(1)或已驳回(5)状态的物品
    """
    
    # 1. 只允许 PUT 请求
    if request.method != 'PUT':
        return JsonResponse({
            'code': 405,
            'msg': '请求方法不允许'
        })
    
    # 2. 获取当前登录用户
    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse({
            'code': 401,
            'msg': '未登录，请先登录'
        })
    
    # 3. 查询物品
    try:
        item = Item.objects.get(id=item_id)
    except Item.DoesNotExist:
        return JsonResponse({
            'code': 404,
            'msg': '物品不存在'
        })
    
    # 4. 权限校验：只有发布者可以修改自己的物品
    if item.user_id != user_id:
        return JsonResponse({
            'code': 403,
            'msg': '无权限修改此物品'
        })
    
    # 5. 状态校验：只有待审核(1)或已驳回(5)状态的物品可以修改
    if item.current_status not in [1, 5]:
        return JsonResponse({
            'code': 400,
            'msg': f'当前状态为{get_status_text(item.current_status)}，不可修改'
        })
    
    # 6. 解析 JSON 数据
    try:
        body = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({
            'code': 400,
            'msg': '请求数据不是合法的 JSON'
        })
    
    # 7. 获取可更新字段
    # 允许更新的字段列表
    updatable_fields = {
        'item_category': 'item_category',       # 1=失物，2=招领
        'item_type': 'item_type',               # category.id
        'name': 'name',
        'location_id': 'location_id',
        'location_detail': 'location_detail',
        'pickup_location': 'pickup_location',
        'happen_time': 'happen_time',
        'feature': 'feature',
        'reward_amount': 'reward_amount',
        'reward_desc': 'reward_desc',
        'contact_name': 'contact_name',
        'contact_phone': 'contact_phone',
    }
    
    # 8. 逐个更新字段
    updated_fields = []
    
    for field_name, model_field in updatable_fields.items():
        if field_name in body:
            # 特殊处理时间字段
            if field_name == 'happen_time':
                try:
                    happen_time_str = body[field_name]
                    if happen_time_str:
                        # 尝试解析多种时间格式
                        try:
                            happen_time = datetime.strptime(happen_time_str, '%Y-%m-%dT%H:%M:%S')
                        except ValueError:
                            try:
                                happen_time = datetime.strptime(happen_time_str, '%Y-%m-%d %H:%M:%S')
                            except ValueError:
                                # 如果前端使用datetime-local的格式
                                happen_time_str = happen_time_str.replace('T', ' ')
                                if '.' in happen_time_str:
                                    happen_time_str = happen_time_str.split('.')[0]
                                happen_time = datetime.strptime(happen_time_str, '%Y-%m-%d %H:%M:%S')
                        setattr(item, model_field, happen_time)
                        updated_fields.append(field_name)
                except Exception as e:
                    return JsonResponse({
                        'code': 400,
                        'msg': f'{field_name} 时间格式错误，应为 YYYY-MM-DD HH:MM:SS',
                        'error': str(e)
                    })
            
            # 特殊处理分类字段：如果是招领信息，不能有悬赏
            elif field_name == 'item_category':
                new_category = body[field_name]
                if new_category == 2:  # 招领
                    item.reward_amount = 0
                    item.reward_desc = ''
                    updated_fields.append('reward_amount')
                    updated_fields.append('reward_desc')
                setattr(item, model_field, new_category)
                updated_fields.append(field_name)
            
            # 特殊处理悬赏金额：如果是招领信息，悬赏金额必须为0
            elif field_name == 'reward_amount':
                if item.item_category == 2:  # 招领信息不能有悬赏
                    item.reward_amount = 0
                else:
                    setattr(item, model_field, body[field_name] or 0)
                updated_fields.append(field_name)
            
            # 特殊处理悬赏描述：如果是招领信息，悬赏描述必须为空
            elif field_name == 'reward_desc':
                if item.item_category == 2:  # 招领信息不能有悬赏
                    item.reward_desc = ''
                else:
                    setattr(item, model_field, body[field_name] or '')
                updated_fields.append(field_name)
            
            # 其他普通字段
            else:
                setattr(item, model_field, body[field_name])
                updated_fields.append(field_name)
    
    # 9. 如果没有任何字段被更新，直接返回成功
    if not updated_fields:
        return JsonResponse({
            'code': 200,
            'msg': '未修改任何信息'
        })
    
    # 10. 如果是已驳回状态，修改后自动变回待审核状态
    if item.current_status == 5:
        item.current_status = 1  # 变回待审核
        item.reject_reason = None  # 清除驳回原因
        updated_fields.append('current_status')
        updated_fields.append('reject_reason')
    
    # 11. 更新更新时间
    item.update_time = timezone.now()
    
    # 12. 保存修改
    try:
        item.save()
    except Exception as e:
        return JsonResponse({
            'code': 500,
            'msg': '保存失败',
            'error': str(e)
        })
    
    # 13. 记录状态历史（如果是已驳回变回待审核）
    if item.current_status == 1 and 5 in [field for field in updated_fields if field == 'current_status']:
        try:
            ItemStatusHistory.objects.create(
                item_id=item.id,
                old_status=5,  # 已驳回
                new_status=1,  # 待审核
                operator_id=user_id,
                operator_type=1,  # 1=用户
                operate_reason='用户修改信息后重新提交',
                operate_time=timezone.now()
            )
        except Exception as e:
            # 状态历史记录失败不影响主流程
            print(f"记录状态历史失败: {e}")
    
    # 14. 返回结果
    return JsonResponse({
        'code': 200,
        'msg': '修改成功',
        'data': {
            'itemId': item.id,
            'updatedFields': updated_fields
        }
    })


def get_status_text(status):
    """获取状态文本"""
    status_map = {
        1: '待审核',
        2: '已通过',
        3: '已匹配',
        4: '已认领',
        5: '已驳回',
        6: '已取消',
        7: '已归档',
        8: '无效'
    }
    return status_map.get(status, '未知状态')

@csrf_exempt
def delete_item(request, item_id):
    """
    删除物品
    URL: DELETE /api/item/{item_id}
    说明：用户只能删除自己发布的物品，且只能删除待审核(1)、已驳回(5)、已取消(6)状态的物品
    """
    
    # 1. 只允许 DELETE 请求
    if request.method != 'DELETE':
        return JsonResponse({
            'code': 405,
            'msg': '请求方法不允许'
        })
    
    # 2. 获取当前登录用户
    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse({
            'code': 401,
            'msg': '未登录，请先登录'
        })
    
    # 3. 查询物品
    try:
        item = Item.objects.get(id=item_id)
    except Item.DoesNotExist:
        return JsonResponse({
            'code': 404,
            'msg': '物品不存在'
        })
    
    # 4. 权限校验：只有发布者可以删除自己的物品
    if item.user_id != user_id:
        return JsonResponse({
            'code': 403,
            'msg': '无权限删除此物品'
        })
    
    # 5. 状态校验：只允许删除待审核(1)、已驳回(5)、已取消(6)状态的物品
    if item.current_status not in [1, 5, 6]:
        return JsonResponse({
            'code': 400,
            'msg': f'当前状态为{get_status_text(item.current_status)}，不可删除'
        })
    
    # 6. 执行删除
    try:
        # 先删除相关的图片记录（如果有）
        ItemImage.objects.filter(item_id=item_id).delete()
        # 删除状态历史记录（如果有）
        ItemStatusHistory.objects.filter(item_id=item_id).delete()
        # 删除认领记录（如果有）
        Claim.objects.filter(item_id=item_id).delete()
        # 最后删除物品本身
        item.delete()
    except Exception as e:
        return JsonResponse({
            'code': 500,
            'msg': '删除失败',
            'error': str(e)
        })
    
    # 7. 返回结果
    return JsonResponse({
        'code': 200,
        'msg': '删除成功'
    })

@csrf_exempt
def cancel_item(request, item_id):
    """
    取消发布物品（将状态变更为已取消）
    URL: POST /api/item/{item_id}/cancel
    说明：用户只能取消自己发布的物品，且只能取消已通过(2)状态的物品
    """
    
    # 1. 只允许 POST 请求
    if request.method != 'POST':
        return JsonResponse({
            'code': 405,
            'msg': '请求方法不允许'
        })
    
    # 2. 获取当前登录用户
    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse({
            'code': 401,
            'msg': '未登录，请先登录'
        })
    
    # 3. 查询物品
    try:
        item = Item.objects.get(id=item_id)
    except Item.DoesNotExist:
        return JsonResponse({
            'code': 404,
            'msg': '物品不存在'
        })
    
    # 4. 权限校验：只有发布者可以取消自己的物品
    if item.user_id != user_id:
        return JsonResponse({
            'code': 403,
            'msg': '无权限取消此物品'
        })
    
    # 5. 状态校验：只允许取消已通过(2)状态的物品
    if item.current_status != 2:
        return JsonResponse({
            'code': 400,
            'msg': f'当前状态为{get_status_text(item.current_status)}，不可取消发布'
        })
    
    # 6. 记录旧状态
    old_status = item.current_status
    
    # 7. 更新状态为已取消
    item.current_status = 6  # 已取消
    item.update_time = timezone.now()
    
    try:
        item.save()
    except Exception as e:
        return JsonResponse({
            'code': 500,
            'msg': '取消失败',
            'error': str(e)
        })
    
    # 8. 记录状态历史
    try:
        ItemStatusHistory.objects.create(
            item_id=item.id,
            old_status=old_status,
            new_status=6,  # 已取消
            operator_id=user_id,
            operator_type=1,  # 1=用户
            operate_reason='用户主动取消发布',
            operate_time=timezone.now()
        )
    except Exception as e:
        # 状态历史记录失败不影响主流程
        print(f"记录状态历史失败: {e}")
    
    # 9. 返回结果
    return JsonResponse({
        'code': 200,
        'msg': '取消发布成功'
    })


@csrf_exempt
def update_item_images(request, item_id):
    """
    更新物品图片（批量操作）
    URL: POST /api/item/{item_id}/images/update
    说明：删除旧图片，上传新图片，一次性完成
    """
    
    # 1. 只允许 POST 请求
    if request.method != 'POST':
        return JsonResponse({
            'code': 405,
            'msg': '请求方法不允许'
        })
    
    # 2. 获取当前登录用户
    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse({
            'code': 401,
            'msg': '未登录，请先登录'
        })
    
    # 3. 查询物品
    try:
        item = Item.objects.get(id=item_id)
    except Item.DoesNotExist:
        return JsonResponse({
            'code': 404,
            'msg': '物品不存在'
        })
    
    # 4. 权限校验：只有发布者可以更新图片
    if item.user_id != user_id:
        return JsonResponse({
            'code': 403,
            'msg': '无权限更新此物品的图片'
        })
    
    # 5. 删除所有旧图片
    try:
        deleted_count, _ = ItemImage.objects.filter(item_id=item_id).delete()
        print(f"删除了 {deleted_count} 张旧图片")
    except Exception as e:
        return JsonResponse({
            'code': 500,
            'msg': '删除旧图片失败',
            'error': str(e)
        })
    
    # 6. 获取新图片
    images_data = []
    
    # 检查是否是多部分表单数据
    if request.content_type.startswith('multipart/form-data'):
        # 处理上传的图片文件
        files = request.FILES.getlist('images')
        
        if len(files) > 5:
            return JsonResponse({
                'code': 400,
                'msg': '最多只能上传5张图片'
            })
        
        for index, file in enumerate(files):
            if not file.content_type.startswith('image/'):
                return JsonResponse({
                    'code': 400,
                    'msg': '只能上传图片文件'
                })
            
            if file.size > 5 * 1024 * 1024:
                return JsonResponse({
                    'code': 400,
                    'msg': f'图片"{file.name}"大小不能超过5MB'
                })
            
            try:
                # 读取图片二进制
                image_bytes = file.read()
                
                # 创建图片记录
                item_image = ItemImage.objects.create(
                    item_id=item_id,
                    image_data=image_bytes,
                    image_url=file.name,
                    image_type=item.item_category,  # 使用物品类型
                    sort=index + 1
                )
                
                images_data.append({
                    'imageId': item_image.id,
                    'sort': item_image.sort
                })
                
            except Exception as e:
                return JsonResponse({
                    'code': 500,
                    'msg': f'保存图片"{file.name}"失败',
                    'error': str(e)
                })
    
    # 7. 更新物品的更新时间
    item.update_time = timezone.now()
    item.save()
    
    # 8. 返回结果
    return JsonResponse({
        'code': 200,
        'msg': '图片更新成功',
        'data': {
            'deletedCount': deleted_count,
            'uploadedCount': len(images_data),
            'images': images_data
        }
    })


    # ==================== 管理员专用接口 ====================

@require_GET
def get_audit_history(request):
    """
    获取审核历史记录（管理员）
    URL: GET /api/item/audit/history?page=1&size=10&startDate=2026-01-01&endDate=2026-02-28&adminId=1&status=2&itemCategory=1
    支持筛选：时间范围、审核人、审核结果（通过/驳回）、信息类型（失物/招领）
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
            "msg": "无权限查看审核记录"
        })
    
    # 2. 获取参数
    page = int(request.GET.get('page', 1))
    size = int(request.GET.get('size', 10))
    start_date = request.GET.get('startDate')
    end_date = request.GET.get('endDate')
    admin_id = request.GET.get('adminId')
    status = request.GET.get('status')  # 筛选审核结果：2-通过, 5-驳回
    item_category = request.GET.get('itemCategory')  # 1-失物, 2-招领
    keyword = request.GET.get('keyword')  # 物品名称关键词
    
    # 3. 查询所有审核相关的状态历史记录
    # 包括：待审核->已通过(2)、待审核->已驳回(5)
    queryset = ItemStatusHistory.objects.filter(
        old_status=1  # 从待审核状态变更的记录
    ).order_by('-operate_time')
    
    # 4. 按新状态筛选（审核结果）
    if status:
        queryset = queryset.filter(new_status=status)
    
    # 5. 按审核人筛选
    if admin_id:
        queryset = queryset.filter(operator_id=admin_id)
    
    # 6. 时间范围筛选
    if start_date:
        queryset = queryset.filter(operate_time__gte=start_date)
    if end_date:
        queryset = queryset.filter(operate_time__lte=end_date)
    
    # 7. 分页前先获取总数
    total_count = queryset.count()
    
    # 8. 手动分页（因为需要先关联查询物品信息）
    start_index = (page - 1) * size
    end_index = start_index + size
    histories = list(queryset[start_index:end_index])
    
    # 9. 组装数据
    data_list = []
    for history in histories:
        # 查询物品信息
        try:
            item = Item.objects.get(id=history.item_id)
        except Item.DoesNotExist:
            continue  # 跳过已删除的物品
        
        # 按物品类型筛选
        if item_category and str(item.item_category) != str(item_category):
            continue
            
        # 按关键词筛选
        if keyword and keyword not in item.name:
            continue
        
        # 查询操作人信息
        operator = User.objects.filter(id=history.operator_id).first()
        
        # 查询地点名称
        location_name = ""
        if item.location_id:
            location = Location.objects.filter(id=item.location_id).first()
            if location:
                location_name = location.name
        
        # 查询物品图片数量（用于判断照片清晰度审核）
        image_count = ItemImage.objects.filter(item_id=item.id).count()
        
        data_list.append({
            "historyId": history.id,
            "itemId": history.item_id,
            "itemName": item.name,
            "itemCategory": item.item_category,
            "itemCategoryName": "失物" if item.item_category == 1 else "招领",
            "locationName": location_name,
            "oldStatus": history.old_status,
            "oldStatusName": "待审核",
            "newStatus": history.new_status,
            "newStatusName": "已通过" if history.new_status == 2 else "已驳回",
            "operatorId": history.operator_id,
            "operatorName": operator.real_name if operator else "未知",
            "operatorType": history.operator_type,
            "operatorTypeName": "管理员" if history.operator_type == 2 else "用户",
            "reason": history.operate_reason,  # 驳回原因或审核备注
            "operateTime": history.operate_time.strftime('%Y-%m-%d %H:%M:%S'),
            "imageCount": image_count,  # 照片数量（审核时参考）
            "contactName": item.contact_name,
            "contactPhone": item.contact_phone
        })
    
    # 10. 计算实际返回的总数（经过物品筛选后）
    actual_total = len(data_list)
    
    return JsonResponse({
        "code": 200,
        "msg": "success",
        "data": {
            "list": data_list,
            "page": page,
            "size": size,
            "total": actual_total,
            "filters": {
                "startDate": start_date,
                "endDate": end_date,
                "adminId": admin_id,
                "status": status,
                "itemCategory": item_category,
                "keyword": keyword
            }
        }
    })


@csrf_exempt
@require_POST
def update_item_status(request, item_id):
    """
    更新物品状态（管理员专用）
    URL: POST /api/item/{item_id}/status
    Body: {
        "status": 4,  // 3-已匹配, 4-已认领, 7-已归档, 8-无效
        "remark": "物品已归还失主"  // 状态变更备注/归档说明
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
            "msg": "无权限操作"
        })
    
    # 2. 查询物品
    try:
        item = Item.objects.get(id=item_id)
    except Item.DoesNotExist:
        return JsonResponse({
            "code": 404,
            "msg": "物品不存在"
        })
    
    # 3. 解析参数
    try:
        body = json.loads(request.body.decode('utf-8'))
        new_status = body.get('status')
        remark = body.get('remark', '')
    except json.JSONDecodeError:
        return JsonResponse({
            "code": 400,
            "msg": "请求数据不是合法的 JSON"
        })
    
    # 4. 状态合法性校验
    valid_status = [3, 4, 7, 8]  # 已匹配、已认领、已归档、无效
    if new_status not in valid_status:
        return JsonResponse({
            "code": 400,
            "msg": f"非法的状态值，允许的状态: {valid_status}"
        })
    
    # 5. 状态流转校验
    # 已归档和无效只能从特定状态流转
    if new_status == 7 and item.current_status not in [2, 3, 4]:  # 已归档只能从已通过、已匹配、已认领归档
        return JsonResponse({
            "code": 400,
            "msg": "当前状态不可直接归档"
        })
    
    old_status = item.current_status
    
    # 6. 更新状态
    item.current_status = new_status
    item.update_time = timezone.now()
    
    # 7. 如果是归档，记录归档说明
    if new_status == 7:
        item.archive_desc = remark
    
    try:
        item.save()
    except Exception as e:
        return JsonResponse({
            "code": 500,
            "msg": "状态更新失败",
            "error": str(e)
        })
    
    # 8. 记录状态历史
    try:
        ItemStatusHistory.objects.create(
            item_id=item.id,
            old_status=old_status,
            new_status=new_status,
            operator_id=user_id,
            operator_type=2,  # 2=管理员
            operate_reason=remark,
            operate_time=timezone.now()
        )
    except Exception as e:
        print(f"记录状态历史失败: {e}")
    
    return JsonResponse({
        "code": 200,
        "msg": "状态更新成功",
        "data": {
            "itemId": item.id,
            "oldStatus": old_status,
            "newStatus": new_status
        }
    })


@require_GET
def get_long_term_unclaimed(request):
    """
    获取长期无人认领物品列表（超过30天）
    URL: GET /api/item/unclaimed/long-term?days=30
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
            "msg": "无权限查看"
        })
    
    # 2. 获取天数参数（默认30天）
    days = int(request.GET.get('days', 30))
    page = int(request.GET.get('page', 1))
    size = int(request.GET.get('size', 10))
    
    # 3. 计算截止日期
    from datetime import timedelta
    deadline = timezone.now() - timedelta(days=days)
    
    # 4. 查询长期未处理的物品（已通过、已匹配状态，且创建时间超过指定天数）
    queryset = Item.objects.filter(
        current_status__in=[2, 3],  # 已通过、已匹配
        create_time__lte=deadline
    ).order_by('create_time')  # 按时间升序，最早的在前
    
    # 5. 分页
    paginator = Paginator(queryset, size)
    page_obj = paginator.get_page(page)
    
    # 6. 组装数据
    data_list = []
    for item in page_obj:
        # 获取地点名称
        location_name = ""
        if item.location_id:
            location = Location.objects.filter(id=item.location_id).first()
            if location:
                location_name = location.name
        
        # 计算已发布天数
        days_published = (timezone.now() - item.create_time).days
        
        # 获取第一张图片
        first_image = ItemImage.objects.filter(
            item_id=item.id
        ).order_by("sort").first()
        
        first_image_url = None
        if first_image:
            first_image_url = f"/api/item/image/{first_image.id}"
        
        data_list.append({
            "itemId": item.id,
            "name": item.name,
            "itemCategory": item.item_category,
            "locationName": location_name,
            "createTime": item.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            "daysPublished": days_published,
            "currentStatus": item.current_status,
            "contactName": item.contact_name,
            "contactPhone": item.contact_phone,
            "firstImageUrl": first_image_url
        })
    
    return JsonResponse({
        "code": 200,
        "msg": "success",
        "data": {
            "list": data_list,
            "page": page_obj.number,
            "size": size,
            "total": paginator.count,
            "daysThreshold": days
        }
    })


@csrf_exempt
@require_POST
def archive_item(request, item_id):
    """
    归档单个物品（快捷接口）
    URL: POST /api/item/{item_id}/archive
    Body: {
        "archiveDesc": "超过30天无人认领，已移交保卫处"
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
            "msg": "无权限操作"
        })
    
    # 2. 查询物品
    try:
        item = Item.objects.get(id=item_id)
    except Item.DoesNotExist:
        return JsonResponse({
            "code": 404,
            "msg": "物品不存在"
        })
    
    # 3. 解析参数
    try:
        body = json.loads(request.body.decode('utf-8'))
        archive_desc = body.get('archiveDesc', '')
    except json.JSONDecodeError:
        archive_desc = ''
    
    # 4. 状态校验
    if item.current_status not in [2, 3, 4]:
        return JsonResponse({
            "code": 400,
            "msg": "当前状态不可归档"
        })
    
    old_status = item.current_status
    
    # 5. 更新为已归档
    item.current_status = 7  # 已归档
    item.archive_desc = archive_desc
    item.update_time = timezone.now()
    
    try:
        item.save()
    except Exception as e:
        return JsonResponse({
            "code": 500,
            "msg": "归档失败",
            "error": str(e)
        })
    
    # 6. 记录状态历史
    try:
        ItemStatusHistory.objects.create(
            item_id=item.id,
            old_status=old_status,
            new_status=7,
            operator_id=user_id,
            operator_type=2,
            operate_reason=f"归档: {archive_desc}",
            operate_time=timezone.now()
        )
    except Exception as e:
        print(f"记录状态历史失败: {e}")
    
    return JsonResponse({
        "code": 200,
        "msg": "归档成功",
        "data": {
            "itemId": item.id,
            "archiveDesc": archive_desc
        }
    })


@require_GET
def get_statistics(request):
    """
    获取失物招领统计数据
    URL: GET /api/statistics/overview?startDate=2026-01-01&endDate=2026-02-28
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
            "msg": "无权限查看统计数据"
        })
    
    # 2. 获取时间范围参数
    start_date = request.GET.get('startDate')
    end_date = request.GET.get('endDate')
    
    # 3. 基础查询集
    queryset = Item.objects.all()
    
    # 4. 时间范围筛选
    if start_date:
        queryset = queryset.filter(create_time__gte=start_date)
    if end_date:
        queryset = queryset.filter(create_time__lte=end_date)
    
    # 5. 统计各类数据
    total_published = queryset.count()
    pending_audit = queryset.filter(current_status=1).count()
    approved = queryset.filter(current_status=2).count()
    matched = queryset.filter(current_status=3).count()
    claimed = queryset.filter(current_status=4).count()
    rejected = queryset.filter(current_status=5).count()
    canceled = queryset.filter(current_status=6).count()
    archived = queryset.filter(current_status=7).count()
    invalid = queryset.filter(current_status=8).count()
    
    # 6. 按类型统计
    lost_items = queryset.filter(item_category=1).count()  # 失物
    found_items = queryset.filter(item_category=2).count()  # 招领
    
    # 7. 认领率计算
    claim_rate = 0
    if approved + matched + claimed + archived > 0:
        claim_rate = round(claimed / (approved + matched + claimed + archived) * 100, 2)
    
    # 8. 近期趋势（最近7天每天的新增数量）
    from datetime import timedelta
    trend_data = []
    for i in range(6, -1, -1):
        date = timezone.now().date() - timedelta(days=i)
        count = Item.objects.filter(
            create_time__date=date
        ).count()
        trend_data.append({
            "date": date.strftime('%Y-%m-%d'),
            "count": count
        })
    
    return JsonResponse({
        "code": 200,
        "msg": "success",
        "data": {
            "overview": {
                "totalPublished": total_published,
                "pendingAudit": pending_audit,
                "approved": approved,
                "matched": matched,
                "claimed": claimed,
                "rejected": rejected,
                "canceled": canceled,
                "archived": archived,
                "invalid": invalid
            },
            "byCategory": {
                "lostItems": lost_items,
                "foundItems": found_items
            },
            "claimRate": claim_rate,
            "trend": trend_data,
            "timeRange": {
                "startDate": start_date,
                "endDate": end_date
            }
        }
    })


@require_GET
def export_statistics(request):
    """
    导出统计数据（简化版，返回CSV格式数据）
    URL: GET /api/statistics/export?format=excel&startDate=2026-01-01&endDate=2026-02-28
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
            "msg": "无权限导出数据"
        })
    
    # 2. 获取参数
    export_format = request.GET.get('format', 'excel')  # excel 或 csv
    start_date = request.GET.get('startDate')
    end_date = request.GET.get('endDate')
    
    # 3. 查询数据
    queryset = Item.objects.all().order_by('-create_time')
    
    if start_date:
        queryset = queryset.filter(create_time__gte=start_date)
    if end_date:
        queryset = queryset.filter(create_time__lte=end_date)
    
    # 4. 准备导出数据
    data_list = []
    for item in queryset:
        location_name = ""
        if item.location_id:
            location = Location.objects.filter(id=item.location_id).first()
            if location:
                location_name = location.name
        
        data_list.append({
            "itemId": item.id,
            "name": item.name,
            "category": "失物" if item.item_category == 1 else "招领",
            "status": get_status_text(item.current_status),
            "location": location_name,
            "createTime": item.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            "contactName": item.contact_name,
            "contactPhone": item.contact_phone
        })
    
    # 5. 返回JSON格式（实际项目中可返回Excel文件）
    # 这里简化处理，返回数据供前端生成CSV
    return JsonResponse({
        "code": 200,
        "msg": "success",
        "data": {
            "format": export_format,
            "total": len(data_list),
            "records": data_list,
            "headers": ["物品ID", "物品名称", "信息类型", "状态", "地点", "创建时间", "联系人", "联系电话"]
        }
    })

@csrf_exempt
@require_POST
def batch_archive_items(request):
    """
    批量归档长期无人认领物品
    URL: POST /api/item/batch/archive
    Body: {
        "itemIds": [1, 2, 3],  // 要归档的物品ID列表
        "archiveDesc": "超过30天无人认领，统一移交保卫处处理",
        "archiveType": "移交保卫处"  // 处理方式：移交保卫处/丢弃/捐赠等
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
            "msg": "无权限操作"
        })
    
    # 2. 解析参数
    try:
        body = json.loads(request.body.decode('utf-8'))
        item_ids = body.get('itemIds', [])
        archive_desc = body.get('archiveDesc', '')
        archive_type = body.get('archiveType', '移交保卫处')  # 处理方式
    except json.JSONDecodeError:
        return JsonResponse({
            "code": 400,
            "msg": "请求数据不是合法的 JSON"
        })
    
    if not item_ids:
        return JsonResponse({
            "code": 400,
            "msg": "请选择要归档的物品"
        })
    
    # 3. 验证所有物品
    valid_items = []
    errors = []
    
    for item_id in item_ids:
        try:
            item = Item.objects.get(id=item_id)
            # 检查状态是否允许归档
            if item.current_status not in [2, 3, 4]:  # 已通过、已匹配、已认领
                errors.append({
                    "itemId": item_id,
                    "itemName": item.name,
                    "error": f"当前状态为{get_status_text(item.current_status)}，不可归档"
                })
                continue
            valid_items.append(item)
        except Item.DoesNotExist:
            errors.append({
                "itemId": item_id,
                "error": "物品不存在"
            })
    
    # 4. 批量归档
    archived_count = 0
    archived_items = []
    
    # 组合完整的归档说明（包含处理方式）
    full_archive_desc = f"[{archive_type}] {archive_desc}"
    
    for item in valid_items:
        old_status = item.current_status
        
        try:
            # 更新状态
            item.current_status = 7  # 已归档
            item.archive_desc = full_archive_desc
            item.update_time = timezone.now()
            item.save()
            
            # 记录状态历史
            ItemStatusHistory.objects.create(
                item_id=item.id,
                old_status=old_status,
                new_status=7,
                operator_id=user_id,
                operator_type=2,  # 管理员
                operate_reason=full_archive_desc,
                operate_time=timezone.now()
            )
            
            archived_count += 1
            archived_items.append({
                "itemId": item.id,
                "itemName": item.name,
                "oldStatus": old_status,
                "archiveDesc": full_archive_desc
            })
            
        except Exception as e:
            errors.append({
                "itemId": item.id,
                "itemName": item.name,
                "error": str(e)
            })
    
    return JsonResponse({
        "code": 200,
        "msg": f"成功归档 {archived_count} 个物品",
        "data": {
            "archivedCount": archived_count,
            "errorCount": len(errors),
            "archivedItems": archived_items,
            "errors": errors,
            "archiveType": archive_type,
            "archiveTime": timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    })


@require_GET
def get_claim_list(request):
    """
    获取认领申请列表（管理员）
    URL: GET /api/item/claim/list?page=1&size=10&status=0&itemId=1
    支持筛选：状态、物品ID、申请人、时间范围
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
            "msg": "无权限查看认领申请"
        })
    
    # 2. 获取参数
    page = int(request.GET.get('page', 1))
    size = int(request.GET.get('size', 10))
    status = request.GET.get('status')  # 0-待审核, 1-已通过, 2-已驳回
    item_id = request.GET.get('itemId')
    claim_user_id = request.GET.get('claimUserId')
    start_date = request.GET.get('startDate')
    end_date = request.GET.get('endDate')
    
    # 3. 基础查询
    queryset = Claim.objects.all().order_by('-create_time')
    
    # 4. 筛选条件
    if status:
        queryset = queryset.filter(status=status)
    if item_id:
        queryset = queryset.filter(item_id=item_id)
    if claim_user_id:
        queryset = queryset.filter(claim_user_id=claim_user_id)
    if start_date:
        queryset = queryset.filter(create_time__gte=start_date)
    if end_date:
        queryset = queryset.filter(create_time__lte=end_date)
    
    # 5. 分页
    paginator = Paginator(queryset, size)
    page_obj = paginator.get_page(page)
    
    # 6. 组装数据
    data_list = []
    for claim in page_obj:
        # 查询物品信息
        item = Item.objects.filter(id=claim.item_id).first()
        # 查询申请人信息
        claim_user = User.objects.filter(id=claim.claim_user_id).first()
        # 查询审核人信息
        audit_user = User.objects.filter(id=claim.audit_user_id).first() if claim.audit_user_id else None
        
        data_list.append({
            "claimId": claim.id,
            "itemId": claim.item_id,
            "itemName": item.name if item else "未知",
            "itemCategory": item.item_category if item else None,
            "itemCategoryName": "失物" if item and item.item_category == 1 else "招领" if item else "未知",
            "claimUserId": claim.claim_user_id,
            "claimUserName": claim_user.real_name if claim_user else "未知",
            "claimUserPhone": claim_user.phone if claim_user else "",
            "proofFeature": claim.proof_feature,  # 认领人提供的证明特征
            "status": claim.status,
            "statusName": {0: '待审核', 1: '已通过', 2: '已驳回'}.get(claim.status, '未知'),
            "rejectReason": claim.reject_reason,
            "auditUserId": claim.audit_user_id,
            "auditUserName": audit_user.real_name if audit_user else None,
            "auditTime": claim.audit_time.strftime('%Y-%m-%d %H:%M:%S') if claim.audit_time else None,
            "claimTime": claim.claim_time.strftime('%Y-%m-%d %H:%M:%S') if claim.claim_time else None,
            "createTime": claim.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            "updateTime": claim.update_time.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    # 7. 统计各状态数量
    status_stats = {
        "pending": Claim.objects.filter(status=0).count(),
        "approved": Claim.objects.filter(status=1).count(),
        "rejected": Claim.objects.filter(status=2).count(),
        "total": Claim.objects.count()
    }
    
    return JsonResponse({
        "code": 200,
        "msg": "success",
        "data": {
            "list": data_list,
            "page": page_obj.number,
            "size": size,
            "total": paginator.count,
            "statistics": status_stats
        }
    })


@csrf_exempt
@require_POST
def audit_claim(request, claim_id):
    """
    审核认领申请（管理员）
    URL: POST /api/claim/{claim_id}/audit
    Body: {
        "status": 1,  // 1-通过, 2-驳回
        "rejectReason": "特征描述不符"  // 驳回时必填
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
            "msg": "无权限审核认领申请"
        })
    
    # 2. 查询认领申请
    try:
        claim = Claim.objects.get(id=claim_id)
    except Claim.DoesNotExist:
        return JsonResponse({
            "code": 404,
            "msg": "认领申请不存在"
        })
    
    # 3. 解析参数
    try:
        body = json.loads(request.body.decode('utf-8'))
        status = body.get('status')
        reject_reason = body.get('rejectReason', '')
    except json.JSONDecodeError:
        return JsonResponse({
            "code": 400,
            "msg": "请求数据不是合法的 JSON"
        })
    
    # 4. 参数校验
    if status not in [1, 2]:
        return JsonResponse({
            "code": 400,
            "msg": "非法的状态值，1-通过, 2-驳回"
        })
    
    if status == 2 and not reject_reason:
        return JsonResponse({
            "code": 400,
            "msg": "驳回时必须填写驳回原因"
        })
    
    # 5. 状态校验
    if claim.status != 0:
        return JsonResponse({
            "code": 400,
            "msg": "该认领申请已处理，不可重复审核"
        })
    
    # 6. 查询关联物品
    try:
        item = Item.objects.get(id=claim.item_id)
    except Item.DoesNotExist:
        return JsonResponse({
            "code": 404,
            "msg": "关联物品不存在"
        })
    
    # 7. 更新认领申请
    claim.status = status
    claim.audit_user_id = user_id
    claim.audit_time = timezone.now()
    
    if status == 2:
        claim.reject_reason = reject_reason
    
    # 如果通过，记录认领时间
    if status == 1:
        claim.claim_time = timezone.now()
    
    try:
        claim.save()
    except Exception as e:
        return JsonResponse({
            "code": 500,
            "msg": "审核失败",
            "error": str(e)
        })
    
    # 8. 如果审核通过，更新物品状态为已认领(4)
    if status == 1:
        old_status = item.current_status
        item.current_status = 4  # 已认领
        item.update_time = timezone.now()
        item.save()
        
        # 记录物品状态历史
        ItemStatusHistory.objects.create(
            item_id=item.id,
            old_status=old_status,
            new_status=4,
            operator_id=user_id,
            operator_type=2,
            operate_reason=f"认领申请通过，认领人ID: {claim.claim_user_id}",
            operate_time=timezone.now()
        )
        
        # 发送通知给认领人（通过时）
        Notification.objects.create(
            user_id=claim.claim_user_id,
            title="认领申请已通过",
            content=f"您对物品【{item.name}】的认领申请已通过审核，请联系管理员领取。",
            type=2,  # 认领相关
            related_id=item.id
        )
    elif status == 2:
        # 发送通知给认领人（驳回时）
        Notification.objects.create(
            user_id=claim.claim_user_id,
            title="认领申请已驳回",
            content=f"您对物品【{item.name}】的认领申请未通过审核。驳回原因：{reject_reason}",
            type=2,  # 认领相关
            related_id=item.id
        )
    
    return JsonResponse({
        "code": 200,
        "msg": "审核成功",
        "data": {
            "claimId": claim.id,
            "status": status,
            "statusName": "已通过" if status == 1 else "已驳回",
            "itemId": item.id,
            "itemName": item.name,
            "auditTime": claim.audit_time.strftime('%Y-%m-%d %H:%M:%S')
        }
    })


@require_GET
def admin_item_list(request):
    """
    管理员专用物品列表查询（支持多种条件筛选）
    URL: GET /api/item/admin/list?page=1&size=10&status=2&itemCategory=1&locationId=201&startDate=2026-01-01&endDate=2026-02-28&keyword=手机&hasReward=true&sortField=createTime&sortOrder=desc
    支持筛选：状态、类型、地点、时间范围、关键词、是否有悬赏、排序方式
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
            "msg": "无权限查看"
        })
    
    # 2. 获取所有参数
    page = int(request.GET.get('page', 1))
    size = int(request.GET.get('size', 10))
    status = request.GET.get('status')  # 状态筛选，支持多个：1,2,3
    item_category = request.GET.get('itemCategory')  # 1-失物, 2-招领
    location_id = request.GET.get('locationId')
    start_date = request.GET.get('startDate')
    end_date = request.GET.get('endDate')
    keyword = request.GET.get('keyword')  # 物品名称关键词
    has_reward = request.GET.get('hasReward')  # true-有悬赏
    contact_name = request.GET.get('contactName')  # 联系人姓名
    contact_phone = request.GET.get('contactPhone')  # 联系人电话
    sort_field = request.GET.get('sortField', 'createTime')  # 排序字段
    sort_order = request.GET.get('sortOrder', 'desc')  # asc/desc
    
    # 3. 基础查询
    queryset = Item.objects.all()
    
    # 4. 状态筛选（支持多个状态，逗号分隔）
    if status:
        if status != 'all':
            status_list = [int(s) for s in status.split(',') if s.isdigit()]
            if status_list:
                queryset = queryset.filter(current_status__in=status_list)
    
    # 5. 其他筛选条件
    if item_category:
        queryset = queryset.filter(item_category=item_category)
    if location_id:
        # 如果location_id是单个数字（1-4），表示按校区筛选
        # 1xxxx = 朝晖校区, 2xxxx = 屏峰校区, 3xxxx = 莫干山校区, 4xxxx = 西湖校区
        if location_id in ['1', '2', '3', '4']:
            # 使用范围查询，性能更好
            campus_prefix = int(location_id)
            min_id = campus_prefix * 10000
            max_id = (campus_prefix + 1) * 10000
            queryset = queryset.filter(location_id__gte=min_id, location_id__lt=max_id)
        else:
            # 否则按精确的location_id筛选
            queryset = queryset.filter(location_id=location_id)
    if start_date:
        queryset = queryset.filter(create_time__gte=start_date)
    if end_date:
        queryset = queryset.filter(create_time__lte=end_date)
    if keyword:
        queryset = queryset.filter(name__icontains=keyword)
    if has_reward == 'true':
        queryset = queryset.filter(reward_amount__gt=0)
    if contact_name:
        queryset = queryset.filter(contact_name__icontains=contact_name)
    if contact_phone:
        queryset = queryset.filter(contact_phone__icontains=contact_phone)
    
    # 6. 排序
    order_prefix = '-' if sort_order == 'desc' else ''
    if sort_field == 'createTime':
        queryset = queryset.order_by(f'{order_prefix}create_time')
    elif sort_field == 'happenTime':
        queryset = queryset.order_by(f'{order_prefix}happen_time')
    elif sort_field == 'rewardAmount':
        queryset = queryset.order_by(f'{order_prefix}reward_amount')
    else:
        queryset = queryset.order_by(f'{order_prefix}create_time')
    
    # 7. 分页
    paginator = Paginator(queryset, size)
    page_obj = paginator.get_page(page)
    
    # 8. 组装数据
    data_list = []
    for item in page_obj:
        # 获取地点名称
        location_name = ""
        if item.location_id:
            location = Location.objects.filter(id=item.location_id).first()
            if location:
                location_name = location.name
        
        # 获取分类名称
        category_name = ""
        if item.item_type:
            category = Category.objects.filter(id=item.item_type).first()
            if category:
                category_name = category.name
        
        # 获取第一张图片
        first_image = ItemImage.objects.filter(
            item_id=item.id
        ).order_by("sort").first()
        
        first_image_url = None
        if first_image:
            first_image_url = f"/api/item/image/{first_image.id}"
        
        # 查询认领申请数量
        claim_count = Claim.objects.filter(item_id=item.id).count()
        pending_claim_count = Claim.objects.filter(item_id=item.id, status=0).count()
        
        data_list.append({
            "itemId": item.id,
            "userId": item.user_id,
            "name": item.name,
            "itemCategory": item.item_category,
            "itemCategoryName": "失物" if item.item_category == 1 else "招领",
            "itemType": item.item_type,
            "itemTypeName": category_name,
            "locationId": item.location_id,
            "locationName": location_name,
            "locationDetail": item.location_detail,
            "pickupLocation": item.pickup_location,
            "happenTime": item.happen_time.strftime('%Y-%m-%d %H:%M:%S'),
            "feature": item.feature,
            "rewardAmount": float(item.reward_amount),
            "rewardDesc": item.reward_desc,
            "contactName": item.contact_name,
            "contactPhone": item.contact_phone,
            "currentStatus": item.current_status,
            "currentStatusName": get_status_text(item.current_status),
            "rejectReason": item.reject_reason,
            "archiveDesc": item.archive_desc,
            "auditUserId": item.audit_user_id,
            "auditTime": item.audit_time.strftime('%Y-%m-%d %H:%M:%S') if item.audit_time else None,
            "createTime": item.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            "updateTime": item.update_time.strftime('%Y-%m-%d %H:%M:%S'),
            "firstImageUrl": first_image_url,
            "claimCount": claim_count,  # 认领申请总数
            "pendingClaimCount": pending_claim_count  # 待审核认领数
        })
    
    # 9. 统计各状态数量
    status_stats = {}
    for code, name in ITEM_STATUS.items():
        status_stats[name] = Item.objects.filter(current_status=code).count()
    
    return JsonResponse({
        "code": 200,
        "msg": "success",
        "data": {
            "list": data_list,
            "page": page_obj.number,
            "size": size,
            "total": paginator.count,
            "statistics": status_stats,
            "filters": {
                "status": status,
                "itemCategory": item_category,
                "locationId": location_id,
                "startDate": start_date,
                "endDate": end_date,
                "keyword": keyword,
                "hasReward": has_reward,
                "sortField": sort_field,
                "sortOrder": sort_order
            }
        }
    })




# ==================== 新增：分类管理接口（管理员） ====================

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
def get_admin_category_tree(request):
    """
    获取分类树（管理视角）
    URL: GET /api/item/admin/category/tree?includeDisabled=true
    """
    has_perm, error_response = check_admin_permission(request)
    if not has_perm:
        return error_response
    
    # 是否包含禁用分类
    include_disabled = request.GET.get('includeDisabled', 'false') == 'true'
    
    if include_disabled:
        qs = Category.objects.all().order_by("-sort", "id")
    else:
        qs = Category.objects.filter(status=1).order_by("-sort", "id")
    
    category_list = list(qs.values("id", "name", "parent_id", "sort", "status"))
    
    # 构建树
    tree = build_category_tree(category_list, parent_id=0)
    
    return JsonResponse({
        "code": 200,
        "msg": "success",
        "data": tree
    })


@csrf_exempt
@require_POST
def create_category(request):
    """
    新增分类
    URL: POST /api/item/admin/category
    Body: {
        "name": "电子产品",
        "parentId": 0,  // 0表示一级分类
        "sort": 1
    }
    """
    has_perm, error_response = check_admin_permission(request)
    if not has_perm:
        return error_response
    
    try:
        body = json.loads(request.body.decode('utf-8'))
        name = body.get('name')
        parent_id = body.get('parentId', 0)
        sort = body.get('sort', 0)
        
        if not name:
            return JsonResponse({"code": 400, "msg": "分类名称不能为空"})
        
        # 检查同级分类名是否重复
        if Category.objects.filter(name=name, parent_id=parent_id).exists():
            return JsonResponse({"code": 400, "msg": "该分类下已存在同名分类"})
        
        category = Category.objects.create(
            name=name,
            parent_id=parent_id,
            sort=sort,
            status=1
        )
        
        return JsonResponse({
            "code": 200,
            "msg": "创建成功",
            "data": {
                "categoryId": category.id,
                "name": category.name,
                "parentId": category.parent_id,
                "sort": category.sort
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({"code": 400, "msg": "请求数据不是合法的 JSON"})
    except Exception as e:
        return JsonResponse({"code": 500, "msg": f"创建失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["PUT"])
def update_category(request, category_id):
    """
    修改分类
    URL: PUT /api/item/admin/category/{category_id}
    Body: {
        "name": "新名称",
        "sort": 2,
        "status": 1
    }
    """
    has_perm, error_response = check_admin_permission(request)
    if not has_perm:
        return error_response
    
    try:
        category = Category.objects.get(id=category_id)
    except Category.DoesNotExist:
        return JsonResponse({"code": 404, "msg": "分类不存在"})
    
    try:
        body = json.loads(request.body.decode('utf-8'))
        
        # 更新字段
        if 'name' in body:
            # 检查同级重名
            parent_id = category.parent_id
            new_name = body['name']
            if Category.objects.filter(name=new_name, parent_id=parent_id).exclude(id=category_id).exists():
                return JsonResponse({"code": 400, "msg": "该分类下已存在同名分类"})
            category.name = new_name
        
        if 'sort' in body:
            category.sort = body['sort']
        
        if 'status' in body:
            category.status = body['status']
        
        category.save()
        
        return JsonResponse({
            "code": 200,
            "msg": "修改成功",
            "data": {
                "categoryId": category.id,
                "name": category.name,
                "sort": category.sort,
                "status": category.status
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({"code": 400, "msg": "请求数据不是合法的 JSON"})
    except Exception as e:
        return JsonResponse({"code": 500, "msg": f"修改失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["DELETE"])
def delete_category(request, category_id):
    """
    删除分类
    URL: DELETE /api/item/admin/category/{category_id}/delete
    """
    has_perm, error_response = check_admin_permission(request)
    if not has_perm:
        return error_response
    
    try:
        category = Category.objects.get(id=category_id)
    except Category.DoesNotExist:
        return JsonResponse({"code": 404, "msg": "分类不存在"})
    
    # 检查是否有子分类
    if Category.objects.filter(parent_id=category_id).exists():
        return JsonResponse({"code": 400, "msg": "该分类下存在子分类，无法删除"})
    
    # 检查是否被物品使用
    if Item.objects.filter(item_type=category_id).exists():
        return JsonResponse({"code": 400, "msg": "该分类已被物品使用，无法删除"})
    
    try:
        category.delete()
        return JsonResponse({
            "code": 200,
            "msg": "删除成功",
            "data": {"categoryId": category_id}
        })
    except Exception as e:
        return JsonResponse({"code": 500, "msg": f"删除失败: {str(e)}"})


# ==================== 新增：地点管理接口（管理员） ====================

@require_GET
def get_admin_location_tree(request):
    """
    获取地点树（管理视角）
    URL: GET /api/item/admin/location/tree?includeDisabled=true
    """
    has_perm, error_response = check_admin_permission(request)
    if not has_perm:
        return error_response
    
    include_disabled = request.GET.get('includeDisabled', 'false') == 'true'
    
    if include_disabled:
        qs = Location.objects.all().order_by("-sort", "id")
    else:
        qs = Location.objects.filter(status=1).order_by("-sort", "id")
    
    location_list = list(qs.values("id", "name", "parent_id", "sort", "status"))
    
    tree = build_location_tree(location_list, parent_id=0)
    
    return JsonResponse({
        "code": 200,
        "msg": "success",
        "data": tree
    })


@csrf_exempt
@require_POST
def create_location(request):
    """
    新增地点
    URL: POST /api/item/admin/location
    Body: {
        "name": "图书馆",
        "parentId": 0,
        "sort": 1
    }
    """
    has_perm, error_response = check_admin_permission(request)
    if not has_perm:
        return error_response
    
    try:
        body = json.loads(request.body.decode('utf-8'))
        name = body.get('name')
        parent_id = body.get('parentId', 0)
        sort = body.get('sort', 0)
        
        if not name:
            return JsonResponse({"code": 400, "msg": "地点名称不能为空"})
        
        if Location.objects.filter(name=name, parent_id=parent_id).exists():
            return JsonResponse({"code": 400, "msg": "该地点下已存在同名地点"})
        
        location = Location.objects.create(
            name=name,
            parent_id=parent_id,
            sort=sort,
            status=1
        )
        
        return JsonResponse({
            "code": 200,
            "msg": "创建成功",
            "data": {
                "locationId": location.id,
                "name": location.name,
                "parentId": location.parent_id,
                "sort": location.sort
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({"code": 400, "msg": "请求数据不是合法的 JSON"})
    except Exception as e:
        return JsonResponse({"code": 500, "msg": f"创建失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["PUT"])
def update_location(request, location_id):
    """
    修改地点
    URL: PUT /api/item/admin/location/{location_id}
    """
    has_perm, error_response = check_admin_permission(request)
    if not has_perm:
        return error_response
    
    try:
        location = Location.objects.get(id=location_id)
    except Location.DoesNotExist:
        return JsonResponse({"code": 404, "msg": "地点不存在"})
    
    try:
        body = json.loads(request.body.decode('utf-8'))
        
        if 'name' in body:
            parent_id = location.parent_id
            new_name = body['name']
            if Location.objects.filter(name=new_name, parent_id=parent_id).exclude(id=location_id).exists():
                return JsonResponse({"code": 400, "msg": "该地点下已存在同名地点"})
            location.name = new_name
        
        if 'sort' in body:
            location.sort = body['sort']
        
        if 'status' in body:
            location.status = body['status']
        
        location.save()
        
        return JsonResponse({
            "code": 200,
            "msg": "修改成功",
            "data": {
                "locationId": location.id,
                "name": location.name,
                "sort": location.sort,
                "status": location.status
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({"code": 400, "msg": "请求数据不是合法的 JSON"})
    except Exception as e:
        return JsonResponse({"code": 500, "msg": f"修改失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["DELETE"])
def delete_location(request, location_id):
    """
    删除地点
    URL: DELETE /api/item/admin/location/{location_id}/delete
    """
    has_perm, error_response = check_admin_permission(request)
    if not has_perm:
        return error_response
    
    try:
        location = Location.objects.get(id=location_id)
    except Location.DoesNotExist:
        return JsonResponse({"code": 404, "msg": "地点不存在"})
    
    # 检查是否有子地点
    if Location.objects.filter(parent_id=location_id).exists():
        return JsonResponse({"code": 400, "msg": "该地点下存在子地点，无法删除"})
    
    # 检查是否被物品使用
    if Item.objects.filter(location_id=location_id).exists():
        return JsonResponse({"code": 400, "msg": "该地点已被物品使用，无法删除"})
    
    try:
        location.delete()
        return JsonResponse({
            "code": 200,
            "msg": "删除成功",
            "data": {"locationId": location_id}
        })
    except Exception as e:
        return JsonResponse({"code": 500, "msg": f"删除失败: {str(e)}"})