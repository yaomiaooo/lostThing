from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
import json


from items.models import Item
from user.models import User
from chat.models import Conversation, Message



@csrf_exempt
def enter_conversation(request):
    """
    进入或创建会话（去询问）
    """

    if request.method != 'POST':
        return JsonResponse({
            "code": 1,
            "msg": "只支持 POST 请求",
            "data": None
        })

    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse({
            "code": 401,
            "msg": "未登录",
            "data": None
        })

    try:
        body = json.loads(request.body.decode('utf-8'))
        item_id = body.get('itemId')

        if not item_id:
            return JsonResponse({
                "code": 1,
                "msg": "缺少 itemId",
                "data": None
            })

        try:
            item = Item.objects.get(id=item_id)
        except Item.DoesNotExist:
            return JsonResponse({
                "code": 1,
                "msg": "物品不存在",
                "data": None
            })

        current_user = User.objects.get(id=user_id)

        # 🚫 不能和自己建会话
        if item.user_id == current_user.id:
            return JsonResponse({
                "code": 1,
                "msg": "不能与自己发起会话",
                "data": None
            })

        # 判断角色
        if item.item_category == 1:
            # 失物：发布人是失主
            owner = User.objects.get(id=item.user_id)
            finder = current_user
        else:
            # 招领：发布人是拾主
            finder = User.objects.get(id=item.user_id)
            owner = current_user

        my_role = 'owner' if current_user.id == owner.id else 'finder'

        # ✅ 关键修复：全部使用 *_id
        with transaction.atomic():
            conversation, _ = Conversation.objects.get_or_create(
                item_id=item.id,
                owner_id=owner.id,
                finder_id=finder.id
            )

        return JsonResponse({
            "code": 0,
            "msg": "success",
            "data": {
                "conversationId": conversation.id,
                "itemId": item.id,
                "myRole": my_role,
                "otherRole": 'finder' if my_role == 'owner' else 'owner'
            }
        })

    except json.JSONDecodeError:
        return JsonResponse({
            "code": 1,
            "msg": "JSON 格式错误",
            "data": None
        })
    except Exception as e:
        return JsonResponse({
            "code": 1,
            "msg": f"服务器错误: {str(e)}",
            "data": None
        })



@csrf_exempt
def get_conversation_messages(request):
    """
    获取会话消息列表

    GET /api/chat/conversation/messages?conversationId=1
    """

    # 1. 仅支持 GET
    if request.method != 'GET':
        return JsonResponse({
            "code": 1,
            "msg": "只支持 GET 请求",
            "data": None
        })

    # 2. 登录校验
    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse({
            "code": 401,
            "msg": "未登录",
            "data": None
        })

    conversation_id = request.GET.get('conversationId')
    if not conversation_id:
        return JsonResponse({
            "code": 1,
            "msg": "缺少 conversationId 参数",
            "data": None
        })

    try:
        conversation = Conversation.objects.get(id=conversation_id)
    except Conversation.DoesNotExist:
        return JsonResponse({
            "code": 1,
            "msg": "会话不存在",
            "data": None
        })

    current_user = User.objects.get(id=user_id)

    # 3. 权限校验（失主 / 拾主 / 管理员）
    if (
        current_user.id != conversation.owner_id
        and current_user.id != conversation.finder_id
        and current_user.role != 1  # 假设 role=1 是管理员
    ):
        return JsonResponse({
            "code": 403,
            "msg": "无权查看该会话",
            "data": None
        })

    # 4. 查询消息
    messages = Message.objects.filter(conversation=conversation).order_by('created_at')

    message_list = []
    for msg in messages:
        if msg.sender_id == conversation.owner_id:
            sender_role = 'owner'
        elif msg.sender_id == conversation.finder_id:
            sender_role = 'finder'
        else:
            sender_role = 'admin'

        message_list.append({
            "id": msg.id,
            "senderId": msg.sender_id,
            "senderRole": sender_role,
            "content": msg.content,
            "createdAt": msg.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })

    return JsonResponse({
        "code": 0,
        "msg": "success",
        "data": {
            "conversationId": conversation.id,
            "canSend": True,  # 后续可按物品状态控制
            "messages": message_list
        }
    })


@csrf_exempt
def send_message(request):
    """
    发送消息

    POST /api/chat/conversation/message/send
    {
        "conversationId": 1,
        "content": "你好，请问这是我丢的东西吗？"
    }
    """

    # 1. 仅支持 POST
    if request.method != 'POST':
        return JsonResponse({
            "code": 1,
            "msg": "只支持 POST 请求",
            "data": None
        })

    # 2. 登录校验
    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse({
            "code": 401,
            "msg": "未登录",
            "data": None
        })

    try:
        body = json.loads(request.body.decode('utf-8'))
        conversation_id = body.get('conversationId')
        content = body.get('content')

        if not conversation_id or not content:
            return JsonResponse({
                "code": 1,
                "msg": "参数不能为空",
                "data": None
            })

        try:
            conversation = Conversation.objects.get(id=conversation_id)
        except Conversation.DoesNotExist:
            return JsonResponse({
                "code": 1,
                "msg": "会话不存在",
                "data": None
            })

        current_user = User.objects.get(id=user_id)

        # 3. 权限校验
        if (
            current_user.id != conversation.owner_id
            and current_user.id != conversation.finder_id
            and current_user.role != 1  # 管理员
        ):
            return JsonResponse({
                "code": 403,
                "msg": "无权在该会话中发送消息",
                "data": None
            })

        # 4. 内容审核（预留位置）
        # TODO: 后续可在这里加关键词过滤 / AI 审核
        # 当前阶段：不拦截

        # 5. 创建消息
        Message.objects.create(
            conversation=conversation,
            sender=current_user,
            content=content
        )

        return JsonResponse({
            "code": 0,
            "msg": "发送成功"
        })

    except json.JSONDecodeError:
        return JsonResponse({
            "code": 1,
            "msg": "请求体不是合法 JSON",
            "data": None
        })
    except Exception as e:
        return JsonResponse({
            "code": 1,
            "msg": f"服务器错误: {str(e)}",
            "data": None
        })


from django.db.models import Q
from django.db.models import Max


@csrf_exempt
def get_my_conversations(request):
    """
    获取当前用户的会话列表

    GET /api/chat/conversation/list
    """

    # 1. 仅支持 GET
    if request.method != 'GET':
        return JsonResponse({
            "code": 1,
            "msg": "只支持 GET 请求",
            "data": None
        })

    # 2. 登录校验
    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse({
            "code": 401,
            "msg": "未登录",
            "data": None
        })

    current_user = User.objects.get(id=user_id)

    # 3. 查询参与的会话
    conversations = Conversation.objects.filter(
        Q(owner_id=user_id) | Q(finder_id=user_id)
    ).order_by('-created_at')

    result = []

    for conv in conversations:
        # 我的角色
        if conv.owner_id == user_id:
            my_role = 'owner'
            other_role = 'finder'
        else:
            my_role = 'finder'
            other_role = 'owner'

        # 最近一条消息
        last_msg = conv.messages.order_by('-created_at').first()

        result.append({
            "conversationId": conv.id,
            "itemId": conv.item_id,
            "itemName": conv.item.name if hasattr(conv.item, 'name') else '',
            "myRole": my_role,
            "otherRole": other_role,
            "lastMessage": last_msg.content if last_msg else '',
            "lastTime": last_msg.created_at.strftime('%Y-%m-%d %H:%M:%S') if last_msg else ''
        })

    return JsonResponse({
        "code": 0,
        "msg": "success",
        "data": result
    })


@csrf_exempt
def can_send_message(request):
    """
    判断会话是否还能发送消息

    GET /api/chat/conversation/can-send
    """

    if request.method != 'GET':
        return JsonResponse({
            "code": 1,
            "msg": "只支持 GET 请求",
            "data": None
        })

    # 登录校验
    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse({
            "code": 401,
            "msg": "未登录",
            "data": None
        })

    conversation_id = request.GET.get('conversationId')
    if not conversation_id:
        return JsonResponse({
            "code": 1,
            "msg": "缺少 conversationId",
            "data": None
        })

    try:
        conversation = Conversation.objects.select_related('item').get(id=conversation_id)
    except Conversation.DoesNotExist:
        return JsonResponse({
            "code": 1,
            "msg": "会话不存在",
            "data": None
        })

    # 是否是会话成员
    if user_id not in [conversation.owner_id, conversation.finder_id]:
        return JsonResponse({
            "code": 403,
            "msg": "无权访问该会话",
            "data": None
        })

    item = conversation.item

    """
    例如：
    item.status == 4  表示 已认领 
    """

    if hasattr(item, 'current_status') and item.current_status == 4:
        can_send = False
    else:
        can_send = True

    return JsonResponse({
        "code": 0,
        "msg": "success",
        "data": {
            "canSend": can_send
        }
    })
