<template>
  <div class="settings-page">
    <!-- 纯色背景 -->
    <div class="background-container">
      <div class="solid-background"></div>
    </div>

    <!-- 整体布局：左侧导航 + 右侧主内容 -->
    <div class="layout-container">
      <!-- 左侧导航栏组件 -->
      <Navigation 
        subtitle="欢迎回来^_^"
        active-nav="设置"
        :custom-content="true"
        @logout="handleLogout"
      >
        <template #custom-content>
          <div class="notice-content">
            <div class="notice-title">⚙️ 设置中心</div>
            <div class="notice-desc">
              管理您的账户信息和安全设置<br>
              定期修改密码保护账户安全
            </div>
          </div>
          <div class="notice-time">{{ currentDate }}</div>
        </template>
      </Navigation>

      <!-- 右侧主内容区域 -->
      <main class="main-content">
        <!-- 页面标题 - 参考消息页风格 -->
        <section class="page-header">
          <div class="header-left">
            <h1 class="page-title">设置中心</h1>
            <div class="subtitle">管理您的账户信息和安全设置</div>
          </div>
        </section>

        <!-- 双栏布局 - 直接显示，无外层容器 -->
        <div class="form-content">
          <!-- 左栏：个人信息展示 -->
          <div class="form-left-column">
            <!-- 个人信息卡片 -->
            <div class="form-section bubble">
              <div class="section-header">
                <h3 class="section-title">个人信息</h3>
                <span class="optional-mark">（只读）</span>
              </div>
              
              <div class="info-grid">
                <div class="info-row">
                  <div class="info-item">
                    <span class="info-label">用户名</span>
                    <span class="info-value">{{ userInfo.username || '加载中...' }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">真实姓名</span>
                    <span class="info-value">{{ userInfo.realName || '加载中...' }}</span>
                  </div>
                </div>
                
                <div class="info-row">
                  <div class="info-item">
                    <span class="info-label">手机号码</span>
                    <span class="info-value">{{ userInfo.phone || '未设置' }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">用户角色</span>
                    <span class="info-value role-tag">{{ getRoleText(userInfo.role) }}</span>
                  </div>
                </div>
                
                <div class="info-row">
                  <div class="info-item full-width">
                    <span class="info-label">账户状态</span>
                    <span class="info-value status-badge" :class="getStatusClass(userInfo.status)">
                      {{ getStatusText(userInfo.status) }}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <!-- 联系管理员卡片 -->
            <div class="form-section bubble">
              <div class="section-header">
                <h3 class="section-title">联系管理员</h3>
              </div>
              
              <div class="contact-info-grid">
                <div class="contact-item">
                  <span class="contact-icon">📧</span>
                  <span class="contact-text">admin@lostthing.edu.cn</span>
                </div>
                <div class="contact-item">
                  <span class="contact-icon">📞</span>
                  <span class="contact-text">0571-88320000</span>
                </div>
                <div class="contact-item">
                  <span class="contact-icon">🏢</span>
                  <span class="contact-text">校保卫处失物招领中心</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 右栏：密码修改 -->
          <div class="form-right-column">
            <!-- 密码修改卡片 -->
            <div class="form-section bubble password-section">
              <div class="section-header">
                <h3 class="section-title">密码修改</h3>
                <span class="required-mark">*</span>
              </div>
              
              <form @submit.prevent="handleChangePassword" class="password-form">
                <div class="form-row">
                  <label class="compact-label">原密码</label>
                  <input
                    v-model="passwordForm.oldPassword"
                    type="password"
                    class="compact-input"
                    :class="{ error: passwordErrors.oldPassword }"
                    placeholder="请输入当前密码"
                    :disabled="passwordLoading"
                  />
                  <div v-if="passwordErrors.oldPassword" class="error-message">
                    {{ passwordErrors.oldPassword }}
                  </div>
                </div>
                
                <div class="form-row">
                  <label class="compact-label">新密码</label>
                  <input
                    v-model="passwordForm.newPassword"
                    type="password"
                    class="compact-input"
                    :class="{ error: passwordErrors.newPassword }"
                    placeholder="请输入新密码（至少6位）"
                    :disabled="passwordLoading"
                  />
                  <div v-if="passwordErrors.newPassword" class="error-message">
                    {{ passwordErrors.newPassword }}
                  </div>
                </div>
                
                <div class="form-row">
                  <label class="compact-label">确认新密码</label>
                  <input
                    v-model="passwordForm.confirmPassword"
                    type="password"
                    class="compact-input"
                    :class="{ error: passwordErrors.confirmPassword }"
                    placeholder="请再次输入新密码"
                    :disabled="passwordLoading"
                  />
                  <div v-if="passwordErrors.confirmPassword" class="error-message">
                    {{ passwordErrors.confirmPassword }}
                  </div>
                </div>
                
                <div class="form-actions">
                  <button 
                    type="button" 
                    class="action-btn cancel-btn"
                    @click="resetPasswordForm"
                    :disabled="passwordLoading"
                  >
                    重置
                  </button>
                  <button 
                    type="submit" 
                    class="action-btn submit-btn"
                    :class="{ submitting: passwordLoading }"
                    :disabled="passwordLoading || !isPasswordFormValid"
                  >
                    <span v-if="passwordLoading" class="loading-text">
                      <span class="loading-spinner"></span>
                      修改中...
                    </span>
                    <span v-else>确认修改</span>
                  </button>
                </div>
              </form>
            </div>

            <!-- 在线留言卡片 -->
            <div class="form-section bubble">
              <div class="section-header">
                <h3 class="section-title">在线留言</h3>
              </div>
              
              <form @submit.prevent="handleContactSubmit" class="message-form">
                <div class="form-row">
                  <label class="compact-label">问题类型</label>
                  <select 
                    v-model="contactForm.type" 
                    class="compact-select"
                    :disabled="contactLoading"
                  >
                    <option value="">请选择问题类型</option>
                    <option value="technical">技术问题</option>
                    <option value="usage">使用问题</option>
                    <option value="suggestion">意见建议</option>
                    <option value="other">其他</option>
                  </select>
                </div>
                
                <div class="form-row">
                  <label class="compact-label">问题描述</label>
                  <textarea
                    v-model="contactForm.message"
                    class="compact-textarea"
                    :class="{ error: contactErrors.message }"
                    placeholder="请详细描述您遇到的问题或建议..."
                    rows="3"
                    maxlength="500"
                    :disabled="contactLoading"
                  ></textarea>
                  <div class="textarea-footer">
                    <div v-if="contactErrors.message" class="error-message">
                      {{ contactErrors.message }}
                    </div>
                    <div class="char-counter">{{ contactForm.message.length }}/500</div>
                  </div>
                </div>
                
                <div class="form-actions">
                  <button 
                    type="submit" 
                    class="action-btn submit-btn secondary"
                    :disabled="contactLoading || !isContactFormValid"
                  >
                    <span v-if="contactLoading" class="loading-text">
                      <span class="loading-spinner"></span>
                      发送中...
                    </span>
                    <span v-else>发送留言</span>
                  </button>
                </div>
              </form>
            </div>
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
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import Navigation from './navigation.vue'

const router = useRouter()

/* ================= 用户信息 ================= */
const userInfo = ref({
  id: 0,
  username: '',
  realName: '',
  phone: '',
  role: 0,
  status: 0
})

/* ================= 密码修改表单 ================= */
const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const passwordErrors = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const passwordLoading = ref(false)

/* ================= 联系管理员表单 ================= */
const contactForm = reactive({
  type: '',
  message: ''
})

const contactErrors = reactive({
  message: ''
})

const contactLoading = ref(false)

/* ================= 模态框状态 ================= */
const showSuccessModal = ref(false)
const successMessage = ref('')

/* ================= 计算属性 ================= */
const isPasswordFormValid = computed(() => {
  return passwordForm.oldPassword && 
         passwordForm.newPassword && 
         passwordForm.confirmPassword &&
         passwordForm.newPassword === passwordForm.confirmPassword &&
         passwordForm.newPassword.length >= 6
})

const isContactFormValid = computed(() => {
  return contactForm.type && contactForm.message.trim().length > 0
})

const currentDate = computed(() => {
  const now = new Date()
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`
})

/* ================= 工具函数 ================= */
const getRoleText = (role: number) => {
  const roleMap = {
    1: '学生',
    2: '教师',
    3: '失物招领管理员',
    4: '系统管理员'
  }
  return roleMap[role as keyof typeof roleMap] || '未知角色'
}

const getStatusText = (status: number) => {
  return status === 1 ? '正常' : '禁用'
}

const getStatusClass = (status: number) => {
  return status === 1 ? 'status-active' : 'status-inactive'
}

/* ================= 数据加载 ================= */
const loadUserInfo = async () => {
  try {
    const res = await axios.get('/api/user/info')
    if (res.data.code === 0) {
      userInfo.value = res.data.data
    }
  } catch (error) {
    console.error('加载用户信息失败:', error)
  }
}

/* ================= 密码修改功能 ================= */
const validatePasswordForm = () => {
  Object.keys(passwordErrors).forEach(key => {
    passwordErrors[key as keyof typeof passwordErrors] = ''
  })

  let isValid = true

  if (!passwordForm.oldPassword) {
    passwordErrors.oldPassword = '请输入原密码'
    isValid = false
  }

  if (!passwordForm.newPassword) {
    passwordErrors.newPassword = '请输入新密码'
    isValid = false
  } else if (passwordForm.newPassword.length < 6) {
    passwordErrors.newPassword = '密码长度至少6位'
    isValid = false
  }

  if (!passwordForm.confirmPassword) {
    passwordErrors.confirmPassword = '请确认新密码'
    isValid = false
  } else if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    passwordErrors.confirmPassword = '两次输入的密码不一致'
    isValid = false
  }

  return isValid
}

const handleChangePassword = async () => {
  if (!validatePasswordForm()) return

  passwordLoading.value = true

  try {
    const res = await axios.post('/api/user/password', {
      userId: userInfo.value.id,
      oldPassword: passwordForm.oldPassword,
      newPassword: passwordForm.newPassword
    })

    if (res.data.code === 0) {
      successMessage.value = '密码修改成功'
      showSuccessModal.value = true
      resetPasswordForm()
    } else {
      passwordErrors.oldPassword = res.data.msg || '密码修改失败'
    }
  } catch (error: any) {
    console.error('密码修改失败:', error)
    passwordErrors.oldPassword = error.response?.data?.msg || '网络错误，请重试'
  } finally {
    passwordLoading.value = false
  }
}

const resetPasswordForm = () => {
  passwordForm.oldPassword = ''
  passwordForm.newPassword = ''
  passwordForm.confirmPassword = ''
  Object.keys(passwordErrors).forEach(key => {
    passwordErrors[key as keyof typeof passwordErrors] = ''
  })
}

/* ================= 联系管理员功能 ================= */
const handleContactSubmit = async () => {
  if (!isContactFormValid.value) return

  contactLoading.value = true

  try {
    const res = await axios.post('/api/admin/feedback/submit', {
      type: contactForm.type,
      message: contactForm.message
    })

    if (res.data.code === 200) {
      successMessage.value = res.data.message || '留言发送成功！管理员将在24小时内回复'
      showSuccessModal.value = true
      
      contactForm.type = ''
      contactForm.message = ''
    } else {
      console.error('发送留言失败:', res.data.msg)
    }
  } catch (error: any) {
    console.error('发送留言失败:', error)
    alert(error.response?.data?.message || '网络错误，请重试')
  } finally {
    contactLoading.value = false
  }
}

/* ================= 退出登录 ================= */
const handleLogout = async () => {
  try {
    const userId = userInfo.value.id
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

/* ================= 生命周期 ================= */
onMounted(() => {
  loadUserInfo()
})
</script>

<style scoped>
/* 基础布局 */
.settings-page {
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

/* 页面标题 - 参考消息页 */
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

/* 双栏布局 - 直接显示，无外层容器包裹 */
.form-content {
  display: flex;
  flex-wrap: wrap;
  gap: 25px;
  max-width: 1400px;
  margin: 0 auto;
}

.form-left-column,
.form-right-column {
  flex: 1;
  min-width: 400px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 表单部分通用样式 - 每个模块独立卡片 */
.form-section {
  border-radius: 16px;
  padding: 24px;
  background: rgba(255, 255, 255, 0.35);
  border: 2px solid rgba(166, 124, 82, 0.2);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  backdrop-filter: blur(15px);
}

.form-section:hover {
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.12);
  background: rgba(255, 255, 255, 0.4);
  transform: translateY(-2px);
}

.password-section {
  flex: 1;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 18px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(166, 124, 82, 0.15);
}

.section-title {
  font-family: "Comic Sans MS", cursive;
  font-size: 20px;
  color: #a67c52;
  font-weight: 600;
  margin: 0;
}

.required-mark {
  color: #ff4d4f;
  font-size: 18px;
}

.optional-mark {
  color: rgba(166, 124, 82, 0.5);
  font-size: 14px;
  font-style: italic;
}

/* 个人信息网格 */
.info-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info-row {
  display: flex;
  gap: 15px;
}

.info-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 14px;
  background: rgba(255, 255, 255, 0.4);
  border-radius: 12px;
  border: 1px solid rgba(166, 124, 82, 0.1);
  transition: all 0.3s ease;
}

.info-item:hover {
  background: rgba(255, 255, 255, 0.6);
  transform: translateY(-2px);
}

.info-item.full-width {
  flex: 1 0 100%;
}

.info-label {
  font-family: "Comic Sans MS", cursive;
  font-size: 13px;
  color: rgba(166, 124, 82, 0.7);
  font-weight: 500;
}

.info-value {
  font-family: "Comic Sans MS", cursive;
  font-size: 15px;
  color: #a67c52;
  font-weight: 600;
}

.role-tag {
  display: inline-block;
  padding: 4px 12px;
  background: linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%);
  border-radius: 12px;
  font-size: 13px;
  color: #a67c52;
  width: fit-content;
}

.status-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 500;
  width: fit-content;
}

.status-active {
  background: #f0fff4;
  color: #52c41a;
}

.status-inactive {
  background: #fff1f0;
  color: #ff4d4f;
}

/* 联系信息网格 */
.contact-info-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.contact-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px;
  background: rgba(255, 255, 255, 0.4);
  border-radius: 12px;
  border: 1px solid rgba(166, 124, 82, 0.1);
  transition: all 0.3s ease;
}

.contact-item:hover {
  background: rgba(255, 255, 255, 0.6);
  transform: translateX(8px);
}

.contact-icon {
  font-size: 20px;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(166, 124, 82, 0.1);
  border-radius: 10px;
}

.contact-text {
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
  font-weight: 500;
}

/* 表单行 */
.form-row {
  margin-bottom: 16px;
}

.form-row:last-child {
  margin-bottom: 0;
}

/* 紧凑型标签和输入框 */
.compact-label {
  display: block;
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
  font-weight: 500;
  margin-bottom: 6px;
}

.compact-input,
.compact-select,
.compact-textarea {
  width: 100%;
  padding: 12px 14px;
  border: 1.6px solid rgba(166, 124, 82, 0.4);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.5);
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
  transition: all 0.3s ease;
  outline: none;
  min-height: 44px;
  box-sizing: border-box;
}

.compact-input::placeholder,
.compact-textarea::placeholder {
  color: rgba(166, 124, 82, 0.5);
  font-size: 13px;
}

.compact-input:focus,
.compact-select:focus,
.compact-textarea:focus {
  border-color: rgba(243, 129, 129, 0.7);
  background: rgba(255, 255, 255, 0.8);
  box-shadow: 0 0 0 3px rgba(243, 129, 129, 0.15);
}

.compact-input:disabled,
.compact-select:disabled,
.compact-textarea:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.compact-input.error,
.compact-textarea.error {
  border-color: #ff4d4f;
  background: rgba(255, 77, 79, 0.05);
}

.compact-textarea {
  resize: vertical;
  min-height: 90px;
}

.textarea-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 6px;
}

.char-counter {
  font-family: "Comic Sans MS", cursive;
  font-size: 12px;
  color: rgba(166, 124, 82, 0.6);
  font-style: italic;
}

/* 错误信息 */
.error-message {
  font-family: "Comic Sans MS", cursive;
  font-size: 12px;
  color: #ff4d4f;
  margin-top: 4px;
  line-height: 1.3;
}

/* 表单操作按钮 */
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 20px;
  padding-top: 15px;
  border-top: 1px solid rgba(166, 124, 82, 0.1);
}

.action-btn {
  padding: 12px 24px;
  border-radius: 12px;
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
  min-width: 100px;
}

.cancel-btn {
  background: transparent;
  border: 2px solid rgba(166, 124, 82, 0.4);
  color: #a67c52;
}

.cancel-btn:hover:not(:disabled) {
  border-color: rgba(166, 124, 82, 0.7);
  background: rgba(166, 124, 82, 0.1);
}

.submit-btn {
  background: linear-gradient(to right, #f38181, #f77d5f);
  color: white;
  box-shadow: 0 4px 15px rgba(247, 125, 95, 0.3);
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(247, 125, 95, 0.4);
  background: linear-gradient(to right, #f77d5f, #f38181);
}

.submit-btn.secondary {
  background: linear-gradient(to right, #a67c52, #8b6b3c);
  box-shadow: 0 4px 15px rgba(166, 124, 82, 0.3);
}

.submit-btn.secondary:hover:not(:disabled) {
  box-shadow: 0 6px 20px rgba(166, 124, 82, 0.4);
  background: linear-gradient(to right, #8b6b3c, #a67c52);
}

.submit-btn:disabled,
.cancel-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.submit-btn.submitting {
  opacity: 0.7;
  cursor: not-allowed;
}

.loading-text {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.loading-spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 导航栏自定义内容样式 */
.notice-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.notice-title {
  font-family: "Comic Sans MS", cursive;
  font-size: 16px;
  font-weight: 600;
  color: #a67c52;
}

.notice-desc {
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: rgba(166, 124, 82, 0.8);
  line-height: 1.4;
  text-align: center;
  margin-bottom: 20px;
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding-right: 5px;
  word-wrap: break-word;
}

.notice-time {
  font-family: "Comic Sans MS", cursive;
  font-size: 12px;
  color: rgba(166, 124, 82, 0.6);
  text-align: right;
}

/* 成功提示模态框 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(5px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 20px;
  padding: 32px;
  max-width: 400px;
  width: 90%;
  text-align: center;
  border: 2px solid rgba(166, 124, 82, 0.2);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
}

.modal-header {
  margin-bottom: 20px;
}

.modal-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.modal-title {
  font-family: "Comic Sans MS", cursive;
  font-size: 20px;
  color: #a67c52;
  margin: 0;
  font-weight: 700;
}

.modal-footer {
  display: flex;
  justify-content: center;
}

.modal-btn {
  padding: 12px 32px;
  border-radius: 12px;
  font-family: "Comic Sans MS", cursive;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
}

.modal-btn.primary {
  background: linear-gradient(to right, #f38181, #f77d5f);
  color: white;
}

.modal-btn.primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(247, 125, 95, 0.3);
}

/* 气泡动画效果 */
.bubble {
  animation: bubbleIn 0.6s ease-out;
}

@keyframes bubbleIn {
  0% {
    opacity: 0;
    transform: scale(0.9) translateY(20px);
  }
  100% {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

/* ================= 响应式设计 ================= */

/* 大屏幕适配（1400px以上） */
@media (min-width: 1401px) {
  .form-content {
    max-width: 1600px;
  }
  
  .form-left-column,
  .form-right-column {
    min-width: 450px;
  }
  
  .form-section {
    padding: 28px;
  }
}

/* 中等屏幕适配（992px-1400px） */
@media (min-width: 992px) and (max-width: 1400px) {
  .main-content {
    margin-left: 260px;
    max-width: calc(100vw - 260px);
    padding: 20px;
  }
  
  .form-left-column,
  .form-right-column {
    min-width: 350px;
  }
  
  .page-title {
    font-size: 32px;
  }
}

/* 平板端适配（769px-991px） */
@media (min-width: 769px) and (max-width: 991px) {
  .main-content {
    margin-left: 240px;
    max-width: calc(100vw - 240px);
    padding: 15px;
  }
  
  .form-content {
    flex-direction: column;
    gap: 20px;
  }
  
  .form-left-column,
  .form-right-column {
    min-width: 100%;
  }
  
  .info-row {
    flex-direction: column;
    gap: 10px;
  }
}

/* 移动端（768px以下） */
@media (max-width: 768px) {
  .layout-container {
    flex-direction: column;
  }

  .main-content {
    margin-left: 0;
    max-width: 100vw;
    padding: 20px 15px;
    padding-bottom: 90px;
  }
  
  .page-title {
    font-size: 24px;
  }
  
  .subtitle {
    font-size: 14px;
  }
  
  .form-content {
    flex-direction: column;
    gap: 15px;
  }
  
  .form-left-column,
  .form-right-column {
    min-width: 100%;
    gap: 15px;
  }
  
  .form-section {
    padding: 20px;
  }
  
  .section-title {
    font-size: 18px;
  }
  
  .info-row {
    flex-direction: column;
    gap: 10px;
  }
  
  .form-actions {
    flex-direction: column;
    gap: 10px;
  }
  
  .action-btn {
    width: 100%;
  }
}

/* 小屏幕手机（480px以下） */
@media (max-width: 480px) {
  .main-content {
    padding: 15px 10px;
    padding-bottom: 80px;
  }
  
  .form-section {
    padding: 16px;
  }
  
  .page-title {
    font-size: 22px;
  }
  
  .compact-input,
  .compact-select,
  .compact-textarea {
    font-size: 14px;
    padding: 10px;
    min-height: 40px;
  }
}
</style>