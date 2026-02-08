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

from django.db import transaction
from django.utils.dateparse import parse_datetime

from datetime import datetime




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

        # 5. 更新审核信息
        item.current_status = status
        item.audit_time = timezone.now()
        item.audit_user_id = user_id   # 来自 session

        # 6. 驳回必须写原因
        if status == 5:
            if not reject_reason:
                return JsonResponse({
                    "code": 400,
                    "msg": "驳回时必须填写驳回原因"
                })
            item.reject_reason = reject_reason

        item.save()

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