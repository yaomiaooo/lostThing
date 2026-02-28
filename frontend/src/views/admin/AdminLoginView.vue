<template>
  <div class="admin-login-page">
    <!-- 背景层 -->
    <div class="background-container">
      <div class="solid-background"></div>
    </div>

    <!-- 登录卡片 -->
    <div class="login-card-container">
      <div class="login-card-wrapper">
        <div class="login-card">
          <!-- 标题 -->
          <div class="login-header">
            <h1 class="admin-title">失物招领管理系统</h1>
            <p class="sub-title">管理员登录</p>
          </div>

          <!-- 表单 -->
          <div class="login-form">
            <!-- 工号输入 -->
            <div class="input-group">
              <span class="input-icon">
                <img src="/login/账号.svg" alt="工号" class="icon-svg" />
              </span>
              <input
                v-model="form.username"
                type="text"
                placeholder="请输入工号"
                class="admin-input"
                @focus="onInputFocus"
                @blur="onInputBlur"
              />
            </div>

            <!-- 密码输入 -->
            <div class="input-group">
              <span class="input-icon">
                <img src="/login/密码.svg" alt="密码" class="icon-svg" />
              </span>
              <input
                v-model="form.password"
                type="password"
                placeholder="请输入密码"
                class="admin-input"
                @focus="onInputFocus"
                @blur="onInputBlur"
              />
            </div>

            <!-- 错误提示 -->
            <div v-if="errorMsg" class="error-msg">
              <span class="error-icon">⚠️</span>
              {{ errorMsg }}
            </div>

            <!-- 登录按钮 -->
            <button 
              :disabled="loading" 
              @click="handleLogin"
              class="login-btn"
              :class="{ loading: loading }"
            >
              <span v-if="!loading">登录</span>
              <span v-else class="loading-text">登录中...</span>
            </button>
          </div>

          <!-- 底部信息 -->
          <div class="login-footer">
            <p class="footer-text">仅限失物招领管理员使用</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import request from '@/utils/request'

const router = useRouter()

// 表单数据
const form = reactive({
  username: '',
  password: '',
  loginType: 'item_admin' // 管理员登录类型
})

const loading = ref(false)
const errorMsg = ref('')

// 输入框焦点处理
const onInputFocus = (event: Event) => {
  const input = event.target as HTMLInputElement
  input.parentElement?.classList.add('focused')
}

const onInputBlur = (event: Event) => {
  const input = event.target as HTMLInputElement
  input.parentElement?.classList.remove('focused')
}

// 登录处理
const handleLogin = async () => {
  if (!form.username || !form.password) {
    errorMsg.value = '请输入工号和密码'
    return
  }

  loading.value = true
  errorMsg.value = ''

  try {
    const response = await request.post('/user/login', {
      username: form.username,
      password: form.password,
      loginType: form.loginType
    })

    if (response.code === 0) {
      // 保存用户信息到sessionStorage
      sessionStorage.setItem('userId', response.data.id.toString())
      sessionStorage.setItem('username', response.data.username)
      sessionStorage.setItem('realName', response.data.realName)
      sessionStorage.setItem('role', response.data.role.toString())
      sessionStorage.setItem('firstLogin', response.data.firstLogin.toString())

      // 跳转到管理员首页
      router.push('/admin/dashboard')
    } else {
      errorMsg.value = response.msg || '登录失败'
    }
  } catch (error: any) {
    console.error('登录错误:', error)
    errorMsg.value = error.response?.data?.msg || '网络错误，请稍后重试'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.admin-login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.background-container {
  position: absolute;
  inset: 0;
  z-index: 0;
}

.solid-background {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card-container {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 400px;
  padding: 20px;
}

.login-card-wrapper {
  animation: slideInUp 0.6s ease-out;
}

@keyframes slideInUp {
  from {
    transform: translateY(30px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.login-card {
  background: #fff;
  border-radius: 16px;
  padding: 40px 32px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(10px);
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.admin-title {
  font-size: 24px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 8px 0;
}

.sub-title {
  font-size: 14px;
  color: #666;
  margin: 0;
}

.login-form {
  margin-bottom: 24px;
}

.input-group {
  position: relative;
  margin-bottom: 20px;
  transition: all 0.3s ease;
}

.input-group.focused {
  transform: translateY(-2px);
}

.input-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  z-index: 1;
}

.icon-svg {
  width: 20px;
  height: 20px;
  opacity: 0.6;
}

.admin-input {
  width: 100%;
  padding: 12px 12px 12px 44px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  background: #fafafa;
  transition: all 0.3s ease;
}

.admin-input:focus {
  outline: none;
  border-color: #007bff;
  background: #fff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.1);
}

.admin-input::placeholder {
  color: #999;
}

.error-msg {
  background: #fff5f5;
  border: 1px solid #fed7d7;
  border-radius: 6px;
  padding: 8px 12px;
  margin-bottom: 16px;
  font-size: 13px;
  color: #e53e3e;
  display: flex;
  align-items: center;
  gap: 8px;
}

.error-icon {
  font-size: 14px;
}

.login-btn {
  width: 100%;
  padding: 12px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
}

.login-btn:hover:not(:disabled) {
  background: #0056b3;
  transform: translateY(-1px);
}

.login-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
  transform: none;
}

.login-btn.loading {
  pointer-events: none;
}

.loading-text {
  opacity: 0.8;
}

.login-footer {
  text-align: center;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

.footer-text {
  font-size: 12px;
  color: #999;
  margin: 0;
}

/* 响应式设计 */
@media (max-width: 480px) {
  .login-card-container {
    padding: 16px;
    max-width: 100%;
  }
  
  .login-card {
    padding: 32px 24px;
  }
  
  .admin-title {
    font-size: 20px;
  }
}
</style>