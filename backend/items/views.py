from django.shortcuts import render

# backend/items/views.py

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from django.views.decorators.http import require_GET
from django.core.paginator import Paginator

from django.views.decorators.http import require_POST

from .models import Item, Location, Claim

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

    try:
        # 2. 解析前端传来的 JSON 数据
        body = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({
            'code': 400,
            'msg': '请求数据不是合法的 JSON'
        })

    # 3. 从 JSON 中取参数（参数名严格按接口文档）
    item_category = body.get('itemCategory')     # 1=失物，2=招领
    item_type = body.get('itemType')             # 分类 ID
    name = body.get('name')
    location_id = body.get('locationId')
    happen_time = body.get('happenTime')
    feature = body.get('feature')
    reward_amount = body.get('rewardAmount', 0)
    reward_desc = body.get('rewardDesc', '')
    contact_name = body.get('contactName')
    contact_phone = body.get('contactPhone')

    # 4. 最基本的参数校验（先保证不为空）
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

    try:
        # 5. 创建并保存 Item 对象
        item = Item.objects.create(
            user_id=1,                 # 先写死，后面接登录系统再改
            item_category=item_category,
            item_type=item_type,
            name=name,
            location_id=location_id,
            happen_time=happen_time,
            feature=feature,
            reward_amount=reward_amount,
            reward_desc=reward_desc,
            contact_name=contact_name,
            contact_phone=contact_phone,
            current_status=1,           # 1 = 待审核
            create_time=timezone.now(),
            update_time=timezone.now()
        )
    except Exception as e:
        return JsonResponse({
            'code': 500,
            'msg': '保存失败',
            'error': str(e)
        })

    # 6. 返回成功结果
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

    查询参数（URL）：
    - itemCategory: 1=失物，2=招领
    - itemType: 分类ID
    - locationId: 地点ID
    - page: 页码（默认 1）
    - size: 每页条数（默认 10）
    """

    # ========= 1. 获取查询参数 =========
    item_category = request.GET.get('itemCategory')
    item_type = request.GET.get('itemType')
    location_id = request.GET.get('locationId')

    page = request.GET.get('page', 1)
    size = request.GET.get('size', 10)

    # ========= 2. 查询数据库（基础查询） =========
    queryset = Item.objects.all().order_by('-create_time')

    # ========= 3. 按条件过滤 =========
    if item_category:
        queryset = queryset.filter(item_category=item_category)

    if item_type:
        queryset = queryset.filter(item_type=item_type)

    if location_id:
        queryset = queryset.filter(location_id=location_id)

    # ========= 4. 分页处理 =========
    paginator = Paginator(queryset, size)
    page_obj = paginator.get_page(page)

    # ========= 5. 组装返回数据 =========
    data_list = []

    for item in page_obj:
        # 查询地点名称（如果存在）
        location_name = ""
        if item.location_id:
            location = Location.objects.filter(id=item.location_id).first()
            if location:
                location_name = location.name

        data_list.append({
            "itemId": item.id,
            "name": item.name,
            "itemCategory": item.item_category,
            "itemType": item.item_type,
            "locationId": item.location_id,
            "locationName": location_name,
            "happenTime": item.happen_time.strftime('%Y-%m-%d %H:%M:%S'),
            "rewardAmount": float(item.reward_amount),
        })

    # ========= 6. 返回统一 JSON =========
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

    # 1. 取参数
    item_id = request.GET.get("itemId")

    if not item_id:
        return JsonResponse({
            "code": 400,
            "msg": "缺少 itemId 参数"
        })

    # 2. 查数据库
    try:
        item = Item.objects.get(id=item_id)
    except Item.DoesNotExist:
        return JsonResponse({
            "code": 404,
            "msg": "物品不存在"
        })

    # 3. 返回数据
    data = {
        "id": item.id,
        "userId": item.user_id,
        "itemType": item.item_type,
        "itemCategory": item.item_category,
        "name": item.name,
        "locationId": item.location_id,
        "happenTime": item.happen_time.strftime("%Y-%m-%d %H:%M:%S"),
        "feature": item.feature,
        "rewardAmount": float(item.reward_amount),
        "rewardDesc": item.reward_desc,
        "contactName": item.contact_name,
        "contactPhone": item.contact_phone,
        "currentStatus": item.current_status,
        "createTime": item.create_time.strftime("%Y-%m-%d %H:%M:%S")
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

    try:
        # 1. 解析前端传来的 JSON 数据
        body = json.loads(request.body.decode("utf-8"))

        item_id = body.get("itemId")
        status = body.get("status")
        reject_reason = body.get("rejectReason", "")

        # 2. 参数校验（非常重要）
        if not item_id or not status:
            return JsonResponse({
                "code": 400,
                "msg": "参数缺失"
            })

        # 3. 查询物品是否存在
        try:
            item = Item.objects.get(id=item_id)
        except Item.DoesNotExist:
            return JsonResponse({
                "code": 404,
                "msg": "物品不存在"
            })

        # 4. 只允许审核通过(2) 或 驳回(5)
        if status not in [2, 5]:
            return JsonResponse({
                "code": 400,
                "msg": "非法的审核状态"
            })

        # 5. 更新审核相关字段
        item.current_status = status
        item.audit_time = timezone.now()

        # ⚠️ 这里先写死审核人 ID（后面你做登录后再改）
        item.audit_user_id = 1

        # 6. 如果是驳回，必须填写驳回原因
        if status == 5:
            if not reject_reason:
                return JsonResponse({
                    "code": 400,
                    "msg": "驳回时必须填写驳回原因"
                })
            item.reject_reason = reject_reason

        # 7. 保存到数据库
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

    # 1. 只允许 POST 请求
    if request.method != 'POST':
        return JsonResponse({
            "code": 405,
            "msg": "请求方式错误"
        })

    try:
        # 2. 解析 JSON 请求体
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


        # ⚠️ 重点：临时写死认领用户 ID
        claim_user_id = 1   # 先假设用户 1 提交认领

        # 5. 创建认领申请
        Claim.objects.create(
            item_id=item_id,
            claim_user_id=claim_user_id,  # ✅ 关键字段
            proof_feature=proof_feature,
            status=0
        )

        # 6. 返回成功结果
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