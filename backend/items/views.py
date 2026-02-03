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