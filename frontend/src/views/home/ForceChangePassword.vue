<template>
  <div class="force-change-password">
    <!-- 纯色背景 -->
    <div class="background-container">
      <div class="solid-background"></div>
    </div>

    <!-- 整体布局：左侧导航 + 右侧主内容 -->
    <div class="layout-container">
      <!-- 左侧导航栏组件 -->
      <Navigation 
        subtitle="首次登录，请修改密码"
        active-nav="设置"
        :custom-content="true"
        @logout="handleLogout"
      >
        <template #custom-content>
          <div class="notice-content">
            <div class="notice-title">密码安全</div>
            <div class="notice-desc">
              为了您的账户安全<br>
              首次登录必须修改默认密码
            </div>
          </div>
          <div class="notice-time">{{ currentDate }}</div>
        </template>
      </Navigation>

      <!-- 右侧主内容区域 -->
      <main class="main-content">
        <!-- 页面标题 - 参考设置页风格 -->
        <section class="page-header">
          <div class="header-left">
            <h1 class="page-title">首次登录密码修改</h1>
            <div class="subtitle">为了您的账户安全，请设置新的密码</div>
          </div>
        </section>

        <!-- 密码修改卡片 -->
        <div class="password-card-container">
          <div class="password-card bubble">
            <div class="card-header">
              <!-- <div class="header-icon">🔐</div> -->
              <div class="header-text">
                <h3 class="card-title">设置新密码</h3>
                <p class="card-subtitle">请设置一个安全的密码，长度至少6位</p>
              </div>
            </div>
            
            <form @submit.prevent="handleSubmit" class="password-form">
              <div class="form-row">
                <label class="compact-label">新密码</label>
                <input
                  v-model="form.newPassword"
                  type="password"
                  class="compact-input"
                  :class="{ error: errors.newPassword }"
                  placeholder="请输入新密码（至少6位）"
                  :disabled="loading"
                />
                <div v-if="errors.newPassword" class="error-message">
                  {{ errors.newPassword }}
                </div>
              </div>
              
              <div class="form-row">
                <label class="compact-label">确认密码</label>
                <input
                  v-model="form.confirmPassword"
                  type="password"
                  class="compact-input"
                  :class="{ error: errors.confirmPassword }"
                  placeholder="请再次输入新密码"
                  :disabled="loading"
                />
                <div v-if="errors.confirmPassword" class="error-message">
                  {{ errors.confirmPassword }}
                </div>
              </div>
              
              <div class="form-actions">
                <button 
                  type="submit" 
                  class="action-btn submit-btn"
                  :class="{ submitting: loading }"
                  :disabled="loading || !isFormValid"
                >
                  <span v-if="loading" class="loading-text">
                    <span class="loading-spinner"></span>
                    修改中...
                  </span>
                  <span v-else>确认修改</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      </main>
    </div>

    <!-- 成功提示模态框 -->
    <div v-if="showSuccessModal" class="modal-overlay">
      <div class="modal-content bubble">
        <div class="modal-header">
          <div class="modal-icon">✅</div>
          <h3 class="modal-title">{{ successMessage }}</h3>
        </div>
        <div class="modal-footer">
          <button class="modal-btn primary" @click="showSuccessModal = false">确定</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import Navigation from './navigation.vue'

const router = useRouter()
const loading = ref(false)

const form = reactive({
  newPassword: '',
  confirmPassword: ''
})

const errors = reactive({
  newPassword: '',
  confirmPassword: ''
})

/* ================= 计算属性 ================= */
const currentDate = computed(() => {
  const now = new Date()
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`
})

const isFormValid = computed(() => {
  return form.newPassword && 
         form.confirmPassword &&
         form.newPassword === form.confirmPassword &&
         form.newPassword.length >= 6
})

/* ================= 表单验证 ================= */
const validateForm = () => {
  errors.newPassword = ''
  errors.confirmPassword = ''
  
  let valid = true
  
  if (!form.newPassword) {
    errors.newPassword = '请输入新密码'
    valid = false
  } else if (form.newPassword.length < 6) {
    errors.newPassword = '密码长度至少6位'
    valid = false
  }
  
  if (!form.confirmPassword) {
    errors.confirmPassword = '请确认新密码'
    valid = false
  } else if (form.newPassword !== form.confirmPassword) {
    errors.confirmPassword = '两次输入的密码不一致'
    valid = false
  }
  
  return valid
}

const handleSubmit = async () => {
  if (!validateForm()) return
  
  loading.value = true
  
  try {
    const userId = sessionStorage.getItem('userId')
    const res = await axios.post('/api/user/password', {
      userId: userId,
      oldPassword: '123456', // 默认密码
      newPassword: form.newPassword
    })
    
    if (res.data.code === 0) {
      sessionStorage.setItem('firstLogin', '0')
      
      // 使用模态框提示而不是alert
      showSuccessModal.value = true
      successMessage.value = '密码修改成功！'
      
      // 延迟跳转，让用户看到成功提示
      setTimeout(() => {
        const role = sessionStorage.getItem('role')
        if (role === '1') {
          router.push('/home')
        } else if (role === '2') {
          router.push('/admin/dashboard')
        } else if (role === '3') {
          router.push('/system/dashboard')
        } else {
          router.push('/home')
        }
      }, 1500)
    } else {
      errors.newPassword = res.data.msg || '密码修改失败'
    }
  } catch (error: any) {
    errors.newPassword = error.response?.data?.msg || '网络错误，请重试'
  } finally {
    loading.value = false
  }
}

/* ================= 退出登录 ================= */
const handleLogout = async () => {
  try {
    const userId = sessionStorage.getItem('userId')
    if (userId) {
      await axios.post('/api/user/logout', { userId })
    }
  } catch (error) {
    console.error('退出登录失败:', error)
  } finally {
    localStorage.clear()
    sessionStorage.clear()
    router.push('/login')
  }
}

/* ================= 模态框状态 ================= */
const showSuccessModal = ref(false)
const successMessage = ref('')
</script>

<style scoped>
/* 基础布局 */
.force-change-password {
  width: 100vw;
  min-height: 100vh;
  position: relative;
  overflow-x: hidden;
}

/* 背景容器 */
.background-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
  overflow: hidden;
}

/* 纯色背景层 */
.solid-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: #f8f3d4;
  pointer-events: none;
}

/* 整体布局：左侧导航 + 右侧主内容 */
.layout-container {
  position: relative;
  z-index: 2;
  width: 100%;
  min-height: 100vh;
  display: flex;
}

/* ================= 右侧主内容区 ================= */
.main-content {
  flex: 1;
  min-height: 100vh;
  padding: 24px 28px;
  margin-left: 288px;
  max-width: calc(100vw - 288px);
  box-sizing: border-box;
}

/* 页面标题 - 参考设置页 */
.page-header {
  backdrop-filter: blur(15px);
  border-radius: 20px;
  padding: 5px;
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  flex: 1;
}

.page-title {
  font-family: "Comic Sans MS", "Marker Felt", cursive;
  font-size: 36px;
  color: #a67c52;
  font-weight: 700;
  margin-bottom: 8px;
}

.subtitle {
  font-family: "Comic Sans MS", cursive;
  font-size: 18px;
  color: rgba(166, 124, 82, 0.8);
}

/* 密码卡片容器 */
.password-card-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 60vh;
}

.password-card {
  width: 100%;
  max-width: 500px;
  border-radius: 20px;
  padding: 32px;
  background: rgba(255, 255, 255, 0.35);
  border: 2px solid rgba(166, 124, 82, 0.2);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  backdrop-filter: blur(15px);
}

.password-card:hover {
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.12);
  background: rgba(255, 255, 255, 0.4);
  transform: translateY(-2px);
}

/* 卡片头部 */
.card-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 28px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(166, 124, 82, 0.15);
}


.header-text {
  flex: 1;
}

.card-title {
  font-family: "Comic Sans MS", cursive;
  font-size: 24px;
  color: #a67c52;
  font-weight: 600;
  margin: 0 0 8px 0;
}

.card-subtitle {
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: rgba(166, 124, 82, 0.7);
  margin: 0;
}

/* 表单样式 */
.password-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-row {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.compact-label {
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
  font-weight: 500;
}

.compact-input {
  width: 90%;
  padding: 12px 16px;
  border: 2px solid rgba(166, 124, 82, 0.3);
  border-radius: 12px;
  font-size: 14px;
  font-family: "Comic Sans MS", cursive;
  color: #a67c52;
  background: rgba(255, 255, 255, 0.6);
  transition: all 0.3s ease;
}

.compact-input::placeholder {
  color: rgba(166, 124, 82, 0.5);
}

.compact-input:focus {
  outline: none;
  border-color: #f77d5f;
  background: rgba(255, 255, 255, 0.8);
  box-shadow: 0 0 0 3px rgba(247, 125, 95, 0.1);
}

.compact-input.error {
  border-color: #ff4d4f;
  background: rgba(255, 77, 79, 0.05);
}

.compact-input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-message {
  font-family: "Comic Sans MS", cursive;
  font-size: 12px;
  color: #ff4d4f;
  margin-top: 4px;
}

/* 表单操作按钮 */
.form-actions {
  display: flex;
  justify-content: center;
  margin-top: 16px;
}

.action-btn {
  padding: 12px 32px;
  border: none;
  border-radius: 12px;
  font-family: "Comic Sans MS", cursive;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 120px;
}

.submit-btn {
  background: linear-gradient(to right, #f38181, #f77d5f);
  color: white;
  box-shadow: 0 4px 15px rgba(247, 125, 95, 0.3);
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(247, 125, 95, 0.4);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.submitting {
  position: relative;
  color: transparent;
}

.loading-text {
  display: flex;
  align-items: center;
  gap: 8px;
  color: white;
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid transparent;
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 16px;
  padding: 24px;
  max-width: 400px;
  width: 90%;
  text-align: center;
}

.modal-header {
  margin-bottom: 20px;
}

.modal-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.modal-title {
  font-family: "Comic Sans MS", cursive;
  font-size: 18px;
  color: #a67c52;
  margin: 0;
}

.modal-footer {
  display: flex;
  justify-content: center;
  gap: 12px;
}

.modal-btn {
  padding: 8px 24px;
  border: none;
  border-radius: 8px;
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.modal-btn.primary {
  background: #f77d5f;
  color: white;
}

.modal-btn.primary:hover {
  background: #f38181;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .main-content {
    margin-left: 0;
    max-width: 100vw;
    padding: 16px;
  }
  
  .password-card {
    padding: 24px;
    margin: 0 16px;
  }
  
  .page-title {
    font-size: 28px;
  }
  
  .card-header {
    flex-direction: column;
    text-align: center;
    gap: 12px;
  }
  

}

/* 导航组件自定义内容样式 */
.notice-content {
  margin-bottom: 16px;
}

.notice-title {
  font-family: "Comic Sans MS", cursive;
  font-size: 18px;
  color: #a67c52;
  font-weight: 600;
  margin-bottom: 8px;
}

.notice-desc {
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: rgba(166, 124, 82, 0.8);
  line-height: 1.4;
}

.notice-time {
  font-family: "Comic Sans MS", cursive;
  font-size: 12px;
  color: rgba(166, 124, 82, 0.6);
  text-align: right;
}
</style>