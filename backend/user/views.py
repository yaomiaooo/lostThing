from django.shortcuts import render

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import User

from django.contrib.auth.hashers import check_password, make_password


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
            "realName": "齐司礼",
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

        # 密码是哈希存储，使用 check_password 验证
        if not check_password(password, user.password):
            return JsonResponse({"code": 1, "msg": "密码错误", "data": None})

        # ================== 关键：写入 session ==================
        request.session['user_id'] = user.id
        request.session['username'] = user.username
        request.session['role'] = user.role
        request.session.set_expiry(60 * 60 * 2)  # 2 小时过期（可选）
        # ========================================================

        # 登录成功，更新最后登录时间
        user.last_login_time = timezone.now()
        user.save()

        data = {
            "id": user.id,
            "username": user.username,
            "realName": user.real_name,
            "role": user.role,
            "firstLogin": user.first_login
        }

        return JsonResponse({"code": 0, "msg": "success", "data": data})

    except json.JSONDecodeError:
        return JsonResponse({"code": 1, "msg": "请求体不是合法的 JSON", "data": None})
    except Exception as e:
        return JsonResponse({"code": 1, "msg": f"服务器错误: {str(e)}", "data": None})


@csrf_exempt
def get_user_info(request):
    """
    6.3.2 获取当前登录用户信息
    URL: GET /api/user/info?id=1
    返回:
    {
      "code": 0,
      "msg": "success",
      "data": {
        "id": 1,
        "username": "2023123456",
        "realName": "齐司礼",
        "phone": "13800000001",
        "role": 1,
        "status": 1
      }
    }
    """
    if request.method != 'GET':
        return JsonResponse({
            "code": 1,
            "msg": "只支持 GET 请求",
            "data": None
        })

    user_id = request.GET.get('id')
    if not user_id:
        return JsonResponse({
            "code": 1,
            "msg": "缺少用户 id 参数",
            "data": None
        })

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({
            "code": 1,
            "msg": "用户不存在",
            "data": None
        })

    data = {
        "id": user.id,
        "username": user.username,
        "realName": user.real_name,
        "phone": user.phone,
        "role": user.role,
        "status": user.status
    }

    return JsonResponse({
        "code": 0,
        "msg": "success",
        "data": data
    })


@csrf_exempt
def change_password(request):
    """
    6.3.3 修改密码接口（首次登录强制）
    URL: POST /api/user/password
    """
    if request.method != 'POST':
        return JsonResponse({
            "code": 1,
            "msg": "只支持 POST 请求"
        })

    try:
        body = json.loads(request.body.decode('utf-8'))
        user_id = body.get('userId')
        old_password = body.get('oldPassword')
        new_password = body.get('newPassword')

        # 1️、 参数校验
        if not all([user_id, old_password, new_password]):
            return JsonResponse({
                "code": 1,
                "msg": "参数不能为空"
            })

        # 2️、 查询用户
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return JsonResponse({
                "code": 1,
                "msg": "用户不存在"
            })

        # 3️、 校验旧密码
        if not check_password(old_password, user.password):
            return JsonResponse({
                "code": 1,
                "msg": "原密码错误"
            })

        # 4️、 设置新密码（⚠️ 必须加密）
        user.password = make_password(new_password)
        user.first_login = 0              # 首次登录完成
        user.update_time = timezone.now()
        user.save()

        return JsonResponse({
            "code": 0,
            "msg": "密码修改成功"
        })

    except json.JSONDecodeError:
        return JsonResponse({
            "code": 1,
            "msg": "请求体不是合法 JSON"
        })
    except Exception as e:
        return JsonResponse({
            "code": 1,
            "msg": f"服务器错误: {str(e)}"
        })

@csrf_exempt
def logout_user(request):
    """
    6.3.4 用户退出登录
    URL: POST /api/user/logout
    """
    if request.method != 'POST':
        return JsonResponse({
            "code": 1,
            "msg": "只支持 POST 请求"
        })

    try:
        # 解析请求体（可选）
        body = json.loads(request.body.decode('utf-8'))
        user_id = body.get('userId')

        # 当前阶段：不维护服务器登录状态
        # 这里不做任何数据库操作

        return JsonResponse({
            "code": 0,
            "msg": "退出成功"
        })

    except json.JSONDecodeError:
        return JsonResponse({
            "code": 1,
            "msg": "请求体不是合法 JSON"
        })
    except Exception as e:
        return JsonResponse({
            "code": 1,
            "msg": f"服务器错误: {str(e)}"
        })