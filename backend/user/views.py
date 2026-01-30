from django.shortcuts import render

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import User
from django.contrib.auth.hashers import check_password

@csrf_exempt
def login_user(request):
    """
    6.3.1 用户登录接口
    URL: POST /api/user/login
    前端传参：
    {
        "username": "2023123456",
        "password": "123456"
    }
    返回：
    {
        "code": 0,
        "msg": "success",
        "data": {
            "id": 1,
            "username": "2023123456",
            "realName": "张三",
            "role": 1
        }
    }
    """
    if request.method != 'POST':
        return JsonResponse({"code": 1, "msg": "只支持 POST 请求", "data": None})

    try:
        body = json.loads(request.body.decode('utf-8'))
        username = body.get('username')
        password = body.get('password')

        if not username or not password:
            return JsonResponse({"code": 1, "msg": "用户名和密码不能为空", "data": None})

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return JsonResponse({"code": 1, "msg": "用户不存在", "data": None})

        # # 如果密码是明文存储
        # if password != user.password:
        #     return JsonResponse({"code": 1, "msg": "密码错误", "data": None})

        # 如果密码是哈希存储，使用 check_password 验证
        if not check_password(password, user.password):
            return JsonResponse({"code": 1, "msg": "密码错误", "data": None})

        # 登录成功，更新最后登录时间
        user.last_login_time = timezone.now()
        user.save()

        data = {
            "id": user.id,
            "username": user.username,
            "realName": user.real_name,
            "role": user.role
        }

        return JsonResponse({"code": 0, "msg": "success", "data": data})

    except json.JSONDecodeError:
        return JsonResponse({"code": 1, "msg": "请求体不是合法的 JSON", "data": None})
    except Exception as e:
        return JsonResponse({"code": 1, "msg": f"服务器错误: {str(e)}", "data": None})

