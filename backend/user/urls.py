from django.urls import path
from . import views

urlpatterns = [
    # 6.3.1 用户登录
    path('/login', views.login_user, name='login_user'),  # POST /api/user/login
    # 6.3.2 获取当前登录用户信息
    path('/info', views.get_user_info, name='get_user_info'),  # GET /api/user/info?id=1
    # 6.3.3 修改密码接口（首次登录强制）
    path('/password', views.change_password,name="change_password"), # POST /api/user/password
    # 6.3.4 用户退出登录
    path('/logout', views.logout_user, name='logout_user'),  # POST /api/user/logout
    # 管理员重置用户密码（临时接口）
    path('/reset-password', views.reset_password, name='reset_password'),  # POST /api/user/reset-password

     # 获取用户列表（支持分页、筛选、搜索）
    path('/list', views.get_user_list, name='get_user_list'),
    
    # 新增管理员账号
    path('/admin', views.create_admin_user, name='create_admin_user'),
    
    # 获取用户详情
    path('/<int:user_id>', views.get_user_detail, name='get_user_detail'),
    
    # 修改用户状态（禁用/启用）
    path('/<int:user_id>/status', views.update_user_status, name='update_user_status'),
    
    # 删除用户
    path('/<int:user_id>/delete', views.delete_user, name='delete_user'),
]