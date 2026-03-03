from django.shortcuts import render

import json
import io
import csv
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import User
from django.db import models

from django.contrib.auth.hashers import check_password, make_password

# 在文件顶部导入部分添加
from django.core.paginator import Paginator
from django.views.decorators.http import require_GET, require_POST, require_http_methods

@csrf_exempt
def login_user(request):
    """
    用户登录接口
    POST /api/user/login

    前端传参：
    {
        "username": "2023123456",
        "password": "123456",
        "loginType": "user"   // user / item_admin / system_admin
    }

    返回：
    {
        "code": 0,
        "msg": "success",
        "data": {
            "id": 1,
            "username": "2023123456",
            "realName": "齐司礼",
            "role": 1,
            "firstLogin": false
        }
    }
    """

    # 1. 仅允许 POST
    if request.method != 'POST':
        return JsonResponse({
            "code": 1,
            "msg": "只支持 POST 请求",
            "data": None
        })

    try:
        # 2. 解析请求体
        body = json.loads(request.body.decode('utf-8'))
        username = body.get('username')
        password = body.get('password')
        login_type = body.get('loginType')

        # 3. 基础参数校验
        if not username or not password:
            return JsonResponse({
                "code": 1,
                "msg": "用户名和密码不能为空",
                "data": None
            })

        if not login_type:
            return JsonResponse({
                "code": 1,
                "msg": "请选择登录身份",
                "data": None
            })

        # 4. 查询用户
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return JsonResponse({
                "code": 1,
                "msg": "用户不存在",
                "data": None
            })

        # 5. 校验密码（哈希）
        if not check_password(password, user.password):
            return JsonResponse({
                "code": 1,
                "msg": "密码错误",
                "data": None
            })

        # 6. 登录身份 → role 映射（核心安全逻辑）
        LOGIN_TYPE_ROLE_MAP = {
            "user": [1, 2],          # 学生 / 老师
            "item_admin": [3],       # 失物招领管理员
            "system_admin": [4]      # 系统管理员
        }

        allowed_roles = LOGIN_TYPE_ROLE_MAP.get(login_type)

        if not allowed_roles:
            return JsonResponse({
                "code": 1,
                "msg": "非法登录身份",
                "data": None
            })

        if user.role not in allowed_roles:
            return JsonResponse({
                "code": 1,
                "msg": "当前账号无权以该身份登录",
                "data": None
            })

        # 7. 写入 session（登录态）
        request.session['user_id'] = user.id
        request.session['username'] = user.username
        request.session['role'] = user.role
        request.session['firstLogin'] = user.first_login
        
        request.session.set_expiry(60 * 60 * 2)  # 2 小时

        # 8. 更新最后登录时间
        user.last_login_time = timezone.now()
        user.save()

        # 9. 返回数据
        data = {
            "id": user.id,
            "username": user.username,
            "realName": user.real_name,
            "role": user.role,
            "firstLogin": user.first_login
        }

        return JsonResponse({
            "code": 0,
            "msg": "success",
            "data": data
        })

    except json.JSONDecodeError:
        return JsonResponse({
            "code": 1,
            "msg": "请求体不是合法的 JSON",
            "data": None
        })
    except Exception as e:
        return JsonResponse({
            "code": 1,
            "msg": f"服务器错误: {str(e)}",
            "data": None
        })

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

    user_id = request.session.get('user_id')
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
def reset_password(request):
    """
    管理员重置用户密码（临时接口）
    URL: POST /api/user/reset-password
    
    请求参数：
    {
        "targetUserId": 123,      # 要重置密码的用户ID
        "newPassword": "123456",  # 新密码
        "adminPassword": "admin123"  # 管理员密码（用于验证身份）
    }
    """
    if request.method != 'POST':
        return JsonResponse({
            "code": 1,
            "msg": "只支持 POST 请求"
        })

    try:
        body = json.loads(request.body.decode('utf-8'))
        target_user_id = body.get('targetUserId')
        new_password = body.get('newPassword')
        admin_password = body.get('adminPassword')

        # 1. 参数校验
        if not all([target_user_id, new_password, admin_password]):
            return JsonResponse({
                "code": 1,
                "msg": "参数不能为空"
            })

        # 2. 验证管理员身份（通过固定密码验证）
        # 这里使用一个固定的管理员密码进行验证
        ADMIN_VERIFICATION_PASSWORD = "admin123"  # 可以修改这个密码
        
        if admin_password != ADMIN_VERIFICATION_PASSWORD:
            return JsonResponse({
                "code": 1,
                "msg": "管理员密码验证失败"
            })

        # 3. 查询目标用户
        try:
            target_user = User.objects.get(id=target_user_id)
        except User.DoesNotExist:
            return JsonResponse({
                "code": 1,
                "msg": "目标用户不存在"
            })

        # 4. 重置密码
        target_user.password = make_password(new_password)
        target_user.first_login = 1  # 设置为首次登录状态
        target_user.update_time = timezone.now()
        target_user.save()

        return JsonResponse({
            "code": 0,
            "msg": f"用户 {target_user.username} 的密码已重置为: {new_password}"
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




# ==================== 新增：账号与权限管理接口 ====================

def check_admin_permission(request):
    """检查是否为管理员（3=区域管理员，4=系统管理员）"""
    user_id = request.session.get('user_id')
    role = request.session.get('role')
    
    if not user_id:
        return False, JsonResponse({"code": 401, "msg": "未登录"})
    
    if role not in [3, 4]:
        return False, JsonResponse({"code": 403, "msg": "无权限操作"})
    
    return True, None


@require_GET
def get_user_list(request):
    """
    获取用户列表（管理员）
    URL: GET /api/user/list?page=1&size=10&role=1&status=1&keyword=张三
    """
    # 权限检查
    has_perm, error_response = check_admin_permission(request)
    if not has_perm:
        return error_response
    
    # 获取参数
    page = int(request.GET.get('page', 1))
    size = int(request.GET.get('size', 10))
    role = request.GET.get('role')
    status = request.GET.get('status')
    keyword = request.GET.get('keyword')
    
    # 基础查询
    queryset = User.objects.all().order_by('-create_time')
    
    # 筛选
    if role:
        queryset = queryset.filter(role=role)
    if status:
        queryset = queryset.filter(status=status)
    if keyword:
        queryset = queryset.filter(
            models.Q(username__icontains=keyword) |
            models.Q(real_name__icontains=keyword) |
            models.Q(phone__icontains=keyword)
        )
    
    # 分页
    paginator = Paginator(queryset, size)
    page_obj = paginator.get_page(page)
    
    # 组装数据
    data_list = []
    for user in page_obj:
        data_list.append({
            "userId": user.id,
            "username": user.username,
            "realName": user.real_name,
            "phone": user.phone,
            "role": user.role,
            "roleName": {1: "学生", 2: "老师", 3: "区域管理员", 4: "系统管理员"}.get(user.role, "未知"),
            "status": user.status,
            "statusName": "启用" if user.status == 1 else "禁用",
            "firstLogin": user.first_login,
            "createTime": user.create_time.strftime('%Y-%m-%d %H:%M:%S') if user.create_time else None,
            "lastLoginTime": user.last_login_time.strftime('%Y-%m-%d %H:%M:%S') if user.last_login_time else None
        })
    
    return JsonResponse({
        "code": 0,
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
def create_admin_user(request):
    """
    新增管理员账号
    URL: POST /api/user/admin
    Body: {
        "username": "admin001",
        "password": "123456",
        "realName": "管理员",
        "phone": "13800000000",
        "role": 3  // 3=区域管理员, 4=系统管理员
    }
    """
    # 权限检查（仅系统管理员可创建）
    user_id = request.session.get('user_id')
    role = request.session.get('role')
    
    if not user_id:
        return JsonResponse({"code": 401, "msg": "未登录"})
    
    if role != 4:  # 仅系统管理员
        return JsonResponse({"code": 403, "msg": "仅系统管理员可创建管理员账号"})
    
    try:
        body = json.loads(request.body.decode('utf-8'))
        username = body.get('username')
        password = body.get('password')
        real_name = body.get('realName')
        phone = body.get('phone')
        new_role = body.get('role')
        
        # 参数校验
        if not all([username, password, real_name, phone, new_role]):
            return JsonResponse({"code": 1, "msg": "参数不能为空"})
        
        if new_role not in [3, 4]:
            return JsonResponse({"code": 1, "msg": "角色只能是3(区域管理员)或4(系统管理员)"})
        
        # 检查用户名是否已存在
        if User.objects.filter(username=username).exists():
            return JsonResponse({"code": 1, "msg": "用户名已存在"})
        
        # 创建用户
        user = User.objects.create(
            username=username,
            password=make_password(password),
            real_name=real_name,
            phone=phone,
            role=new_role,
            status=1,
            first_login=1,
            create_time=timezone.now(),
            update_time=timezone.now()
        )
        
        return JsonResponse({
            "code": 0,
            "msg": "创建成功",
            "data": {
                "userId": user.id,
                "username": user.username,
                "role": user.role
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({"code": 1, "msg": "请求数据不是合法的 JSON"})
    except Exception as e:
        return JsonResponse({"code": 1, "msg": f"创建失败: {str(e)}"})


@require_GET
def get_user_detail(request, user_id):
    """
    获取用户详情
    URL: GET /api/user/{user_id}
    """
    has_perm, error_response = check_admin_permission(request)
    if not has_perm:
        return error_response
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({"code": 1, "msg": "用户不存在"})
    
    # 统计用户发布的物品数量
    from items.models import Item
    post_count = Item.objects.filter(user_id=user_id).count()
    
    data = {
        "userId": user.id,
        "username": user.username,
        "realName": user.real_name,
        "phone": user.phone,
        "role": user.role,
        "roleName": {1: "学生", 2: "老师", 3: "区域管理员", 4: "系统管理员"}.get(user.role, "未知"),
        "status": user.status,
        "statusName": "启用" if user.status == 1 else "禁用",
        "firstLogin": user.first_login,
        "createTime": user.create_time.strftime('%Y-%m-%d %H:%M:%S') if user.create_time else None,
        "updateTime": user.update_time.strftime('%Y-%m-%d %H:%M:%S') if user.update_time else None,
        "lastLoginTime": user.last_login_time.strftime('%Y-%m-%d %H:%M:%S') if user.last_login_time else None,
        "lastLoginIp": getattr(user, 'last_login_ip', ''),
        "statistics": {
            "postCount": post_count
        }
    }
    
    return JsonResponse({
        "code": 0,
        "msg": "success",
        "data": data
    })


@csrf_exempt
@require_http_methods(["PUT"])
def update_user_status(request, user_id):
    """
    修改用户状态（禁用/启用）
    URL: PUT /api/user/{user_id}/status
    Body: {
        "status": 0,  // 0=禁用, 1=启用
        "reason": "违规操作"  // 可选
    }
    """
    has_perm, error_response = check_admin_permission(request)
    if not has_perm:
        return error_response
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({"code": 1, "msg": "用户不存在"})
    
    # 不能操作自己
    current_user_id = request.session.get('user_id')
    if user.id == current_user_id:
        return JsonResponse({"code": 1, "msg": "不能操作自己的账号"})
    
    # 不能禁用系统管理员（仅系统管理员能操作系统管理员）
    current_role = request.session.get('role')
    if user.role == 4 and current_role != 4:
        return JsonResponse({"code": 403, "msg": "无权限操作系统管理员账号"})
    
    try:
        body = json.loads(request.body.decode('utf-8'))
        new_status = body.get('status')
        reason = body.get('reason', '')
        
        if new_status not in [0, 1]:
            return JsonResponse({"code": 1, "msg": "状态值非法，0=禁用, 1=启用"})
        
        old_status = user.status
        user.status = new_status
        user.update_time = timezone.now()
        user.save()
        
        return JsonResponse({
            "code": 0,
            "msg": "状态修改成功",
            "data": {
                "userId": user.id,
                "oldStatus": old_status,
                "newStatus": new_status,
                "reason": reason
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({"code": 1, "msg": "请求数据不是合法的 JSON"})
    except Exception as e:
        return JsonResponse({"code": 1, "msg": f"操作失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["DELETE"])
def delete_user(request, user_id):
    """
    删除用户
    URL: DELETE /api/user/{user_id}
    """
    has_perm, error_response = check_admin_permission(request)
    if not has_perm:
        return error_response
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({"code": 1, "msg": "用户不存在"})
    
    # 不能删除自己
    current_user_id = request.session.get('user_id')
    if user.id == current_user_id:
        return JsonResponse({"code": 1, "msg": "不能删除自己的账号"})
    
    # 不能删除系统管理员（仅系统管理员能删除系统管理员）
    current_role = request.session.get('role')
    if user.role == 4 and current_role != 4:
        return JsonResponse({"code": 403, "msg": "无权限删除系统管理员账号"})
    
    # 检查用户是否有发布的物品
    from items.models import Item
    has_items = Item.objects.filter(user_id=user_id).exists()
    if has_items:
        return JsonResponse({"code": 1, "msg": "该用户有发布的物品，无法删除"})
    
    try:
        user.delete()
        return JsonResponse({
            "code": 0,
            "msg": "删除成功",
            "data": {
                "userId": user_id
            }
        })
    except Exception as e:
        return JsonResponse({"code": 1, "msg": f"删除失败: {str(e)}"})


@csrf_exempt
@require_POST
def create_regular_user(request):
    """
    新增普通用户（学生/教师）
    URL: POST /api/user/create
    Body: {
        "username": "2023001",
        "password": "123456",
        "realName": "张三",
        "phone": "13800138000",
        "role": 1  // 1=学生, 2=教师
    }
    """
    # 权限检查
    has_perm, error_response = check_admin_permission(request)
    if not has_perm:
        return error_response
    
    try:
        body = json.loads(request.body.decode('utf-8'))
        username = body.get('username')
        password = body.get('password')
        real_name = body.get('realName')
        phone = body.get('phone')
        new_role = body.get('role')
        
        # 参数校验
        if not all([username, password, real_name, phone, new_role]):
            return JsonResponse({"code": 1, "msg": "必填参数不能为空"})
        
        if new_role not in [1, 2]:
            return JsonResponse({"code": 1, "msg": "角色只能是1(学生)或2(教师)"})
        
        # 验证手机号格式
        if len(phone) != 11 or not phone.isdigit():
            return JsonResponse({"code": 1, "msg": "手机号格式不正确"})
        
        # 检查用户名是否已存在
        if User.objects.filter(username=username).exists():
            return JsonResponse({"code": 1, "msg": "用户名已存在"})
        
        # 检查手机号是否已存在
        if User.objects.filter(phone=phone).exists():
            return JsonResponse({"code": 1, "msg": "手机号已存在"})
        
        # 创建用户
        user = User.objects.create(
            username=username,
            password=make_password(password),
            real_name=real_name,
            phone=phone,
            role=new_role,
            status=1,
            first_login=1,
            create_time=timezone.now(),
            update_time=timezone.now()
        )
        
        return JsonResponse({
            "code": 0,
            "msg": "创建成功",
            "data": {
                "userId": user.id,
                "username": user.username,
                "realName": user.real_name,
                "role": user.role
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({"code": 1, "msg": "请求数据不是合法的 JSON"})
    except Exception as e:
        return JsonResponse({"code": 1, "msg": f"创建失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["PUT"])
def update_regular_user(request, user_id):
    """
    更新普通用户信息
    URL: PUT /api/user/{user_id}
    """
    # 权限检查
    has_perm, error_response = check_admin_permission(request)
    if not has_perm:
        return error_response
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({"code": 1, "msg": "用户不存在"})
    
    try:
        body = json.loads(request.body.decode('utf-8'))
        real_name = body.get('realName')
        phone = body.get('phone')
        new_role = body.get('role')
        password = body.get('password')
        status = body.get('status')
        
        # 更新字段
        if real_name is not None:
            user.real_name = real_name
        if phone is not None:
            # 检查手机号是否已被其他用户使用
            if User.objects.filter(phone=phone).exclude(id=user_id).exists():
                return JsonResponse({"code": 1, "msg": "手机号已被其他用户使用"})
            user.phone = phone
        if new_role is not None and new_role in [1, 2]:
            user.role = new_role
        if password is not None and password:
            user.password = make_password(password)
            user.first_login = 1
        if status is not None and status in [0, 1]:
            user.status = status
        
        user.update_time = timezone.now()
        user.save()
        
        return JsonResponse({
            "code": 0,
            "msg": "更新成功",
            "data": {
                "userId": user.id,
                "username": user.username
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({"code": 1, "msg": "请求数据不是合法的 JSON"})
    except Exception as e:
        return JsonResponse({"code": 1, "msg": f"更新失败: {str(e)}"})


@require_GET
def export_users(request):
    """
    导出用户数据
    URL: GET /api/user/export?format=xlsx&role=1&status=1&keyword=张三
    format: xlsx 或 csv
    """
    # 权限检查
    has_perm, error_response = check_admin_permission(request)
    if not has_perm:
        return error_response
    
    # 获取参数
    export_format = request.GET.get('format', 'csv')
    role = request.GET.get('role')
    status = request.GET.get('status')
    keyword = request.GET.get('keyword')
    
    # 基础查询
    queryset = User.objects.all().order_by('-create_time')
    
    # 筛选
    if role:
        queryset = queryset.filter(role=role)
    if status:
        queryset = queryset.filter(status=status)
    if keyword:
        queryset = queryset.filter(
            models.Q(username__icontains=keyword) |
            models.Q(real_name__icontains=keyword) |
            models.Q(phone__icontains=keyword)
        )
    
    # 准备数据
    users_data = []
    for user in queryset:
        users_data.append({
            "用户ID": user.id,
            "用户名": user.username,
            "真实姓名": user.real_name,
            "手机号": user.phone,
            "角色": {1: "学生", 2: "老师", 3: "区域管理员", 4: "系统管理员"}.get(user.role, "未知"),
            "状态": "启用" if user.status == 1 else "禁用",
            "是否首次登录": "是" if user.first_login == 1 else "否",
            "创建时间": user.create_time.strftime('%Y-%m-%d %H:%M:%S') if user.create_time else '',
            "最后登录时间": user.last_login_time.strftime('%Y-%m-%d %H:%M:%S') if user.last_login_time else ''
        })
    
    if export_format == 'csv':
        # 导出 CSV
        response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
        filename = f"用户数据_{timezone.now().strftime('%Y%m%d_%H%M%S')}.csv"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        if users_data:
            writer = csv.DictWriter(response, fieldnames=users_data[0].keys())
            writer.writeheader()
            for row in users_data:
                writer.writerow(row)
        
        return response
    
    else:
        # 导出 Excel (xlsx) - 先使用 CSV 作为默认
        response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
        filename = f"用户数据_{timezone.now().strftime('%Y%m%d_%H%M%S')}.csv"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        if users_data:
            writer = csv.DictWriter(response, fieldnames=users_data[0].keys())
            writer.writeheader()
            for row in users_data:
                writer.writerow(row)
        
        return response


@csrf_exempt
@require_POST
def batch_update_users_status(request):
    """
    批量更新用户状态
    URL: POST /api/user/batch-status
    Body: {
        "userIds": [1, 2, 3],
        "status": 0  // 0=禁用, 1=启用
    }
    """
    has_perm, error_response = check_admin_permission(request)
    if not has_perm:
        return error_response
    
    try:
        body = json.loads(request.body.decode('utf-8'))
        user_ids = body.get('userIds', [])
        new_status = body.get('status')
        
        if not user_ids or new_status not in [0, 1]:
            return JsonResponse({"code": 1, "msg": "参数错误"})
        
        current_user_id = request.session.get('user_id')
        # 不能批量操作自己
        user_ids = [uid for uid in user_ids if uid != current_user_id]
        
        updated_count = User.objects.filter(id__in=user_ids).update(
            status=new_status,
            update_time=timezone.now()
        )
        
        return JsonResponse({
            "code": 0,
            "msg": f"成功更新 {updated_count} 个用户",
            "data": {"updatedCount": updated_count}
        })
        
    except json.JSONDecodeError:
        return JsonResponse({"code": 1, "msg": "请求数据不是合法的 JSON"})
    except Exception as e:
        return JsonResponse({"code": 1, "msg": f"操作失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["DELETE"])
def batch_delete_users(request):
    """
    批量删除用户
    URL: DELETE /api/user/batch-delete
    Body: {
        "userIds": [1, 2, 3]
    }
    """
    has_perm, error_response = check_admin_permission(request)
    if not has_perm:
        return error_response
    
    try:
        body = json.loads(request.body.decode('utf-8'))
        user_ids = body.get('userIds', [])
        
        if not user_ids:
            return JsonResponse({"code": 1, "msg": "请选择要删除的用户"})
        
        current_user_id = request.session.get('user_id')
        # 不能删除自己
        user_ids = [uid for uid in user_ids if uid != current_user_id]
        
        # 检查用户是否有发布的物品
        try:
            from items.models import Item
            users_with_items = Item.objects.filter(user_id__in=user_ids).values_list('user_id', flat=True).distinct()
            if users_with_items:
                return JsonResponse({"code": 1, "msg": f"用户 {list(users_with_items)} 有发布的物品，无法删除"})
        except ImportError:
            pass
        
        deleted_count, _ = User.objects.filter(id__in=user_ids).delete()
        
        return JsonResponse({
            "code": 0,
            "msg": f"成功删除 {deleted_count} 个用户",
            "data": {"deletedCount": deleted_count}
        })
        
    except json.JSONDecodeError:
        return JsonResponse({"code": 1, "msg": "请求数据不是合法的 JSON"})
    except Exception as e:
        return JsonResponse({"code": 1, "msg": f"删除失败: {str(e)}"})