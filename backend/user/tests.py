from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.hashers import make_password
from django.utils import timezone
import json
from .models import User


class UserManagementTests(TestCase):
    """用户管理功能测试"""
    
    def setUp(self):
        """测试前的准备工作"""
        self.client = Client()
        
        # 创建测试系统管理员
        self.admin_user = User.objects.create(
            username='admin001',
            password=make_password('admin123'),
            real_name='系统管理员',
            phone='13900000001',
            role=4,  # 系统管理员
            status=1,
            first_login=0,
            create_time=timezone.now(),
            update_time=timezone.now()
        )
        
        # 创建测试普通用户
        self.test_user = User.objects.create(
            username='2023001',
            password=make_password('123456'),
            real_name='测试学生',
            phone='13800000001',
            role=1,  # 学生
            status=1,
            first_login=1,
            create_time=timezone.now(),
            update_time=timezone.now()
        )
        
        # 登录系统管理员
        session = self.client.session
        session['user_id'] = self.admin_user.id
        session['username'] = self.admin_user.username
        session['role'] = self.admin_user.role
        session.save()
    
    def test_create_regular_user_success(self):
        """测试成功创建普通用户"""
        url = reverse('create_regular_user')
        data = {
            'username': '2023002',
            'password': '123456',
            'realName': '新用户',
            'phone': '13800000002',
            'role': 1
        }
        
        response = self.client.post(
            url,
            json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['code'], 0)
        self.assertIn('userId', response_data['data'])
        
        # 验证用户是否创建成功
        new_user = User.objects.get(username='2023002')
        self.assertEqual(new_user.real_name, '新用户')
        self.assertEqual(new_user.phone, '13800000002')
    
    def test_create_user_duplicate_username(self):
        """测试创建用户时用户名重复"""
        url = reverse('create_regular_user')
        data = {
            'username': '2023001',  # 已存在的用户名
            'password': '123456',
            'realName': '重复用户',
            'phone': '13800000003',
            'role': 1
        }
        
        response = self.client.post(
            url,
            json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['code'], 1)
        self.assertIn('用户名已存在', response_data['msg'])
    
    def test_create_user_duplicate_phone(self):
        """测试创建用户时手机号重复"""
        url = reverse('create_regular_user')
        data = {
            'username': '2023004',
            'password': '123456',
            'realName': '重复手机号用户',
            'phone': '13800000001',  # 已存在的手机号
            'role': 1
        }
        
        response = self.client.post(
            url,
            json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['code'], 1)
        self.assertIn('手机号已存在', response_data['msg'])
    
    def test_create_user_invalid_phone(self):
        """测试创建用户时手机号格式不正确"""
        url = reverse('create_regular_user')
        data = {
            'username': '2023005',
            'password': '123456',
            'realName': '格式错误用户',
            'phone': '12345',  # 格式不正确的手机号
            'role': 1
        }
        
        response = self.client.post(
            url,
            json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['code'], 1)
        self.assertIn('手机号格式不正确', response_data['msg'])
    
    def test_update_user_success(self):
        """测试成功更新用户信息"""
        url = reverse('update_regular_user', args=[self.test_user.id])
        data = {
            'realName': '更新后的姓名'
        }
        
        response = self.client.put(
            url,
            json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['code'], 0)
        
        # 验证用户信息是否更新成功
        updated_user = User.objects.get(id=self.test_user.id)
        self.assertEqual(updated_user.real_name, '更新后的姓名')
    
    def test_export_users_csv(self):
        """测试导出 CSV 格式用户数据"""
        url = reverse('export_users')
        response = self.client.get(f'{url}?format=csv')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv; charset=utf-8-sig')
        self.assertIn('attachment; filename=', response['Content-Disposition'])
        self.assertIn('.csv', response['Content-Disposition'])
    
    def test_export_users_with_filters(self):
        """测试带筛选条件导出用户数据"""
        url = reverse('export_users')
        response = self.client.get(f'{url}?format=csv&role=1&status=1')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv; charset=utf-8-sig')
    
    def test_batch_update_users_status(self):
        """测试批量更新用户状态"""
        # 创建另一个测试用户
        another_user = User.objects.create(
            username='2023006',
            password=make_password('123456'),
            real_name='另一个用户',
            phone='13800000006',
            role=1,
            status=1
        )
        
        url = reverse('batch_update_users_status')
        data = {
            'userIds': [self.test_user.id, another_user.id],
            'status': 0  # 禁用
        }
        
        response = self.client.post(
            url,
            json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['code'], 0)
        
        # 验证用户状态是否更新成功
        self.test_user.refresh_from_db()
        another_user.refresh_from_db()
        self.assertEqual(self.test_user.status, 0)
        self.assertEqual(another_user.status, 0)
    
    def test_unauthorized_access(self):
        """测试未登录或无权限访问"""
        # 清除 session
        self.client.session.flush()
        
        # 尝试创建用户
        url = reverse('create_regular_user')
        data = {
            'username': '2023007',
            'password': '123456',
            'realName': '未授权用户',
            'phone': '13800000007',
            'role': 1
        }
        
        response = self.client.post(
            url,
            json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertIn(response_data['code'], [401, 403])


class UserModelTests(TestCase):
    """用户模型测试"""
    
    def test_create_user(self):
        """测试创建用户模型实例"""
        user = User.objects.create(
            username='test001',
            password=make_password('test123'),
            real_name='测试用户',
            phone='13900000000',
            role=1,
            status=1
        )
        
        self.assertEqual(user.username, 'test001')
        self.assertEqual(user.real_name, '测试用户')
        self.assertEqual(user.phone, '13900000000')
        self.assertEqual(user.role, 1)
        self.assertEqual(user.status, 1)
        self.assertTrue(user.first_login)  # 默认应该是首次登录
    
    def test_user_str_representation(self):
        """测试用户模型的字符串表示"""
        user = User.objects.create(
            username='test002',
            password=make_password('test123'),
            real_name='测试用户2',
            phone='13900000001',
            role=2,
            status=1
        )
        
        # 虽然模型没有定义 __str__，但我们可以测试基本属性
        self.assertEqual(user.real_name, '测试用户2')
