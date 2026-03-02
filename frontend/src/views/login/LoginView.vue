<template>
  <div class="login-page">
    <!-- 背景图片 -->
    <div class="background-container">
      <img 
        src="/login/login_background.png" 
        alt="登录背景" 
        class="background-image"
        :class="{ 'background-loaded': backgroundLoaded }"
      />
      <!-- 预渲染的毛玻璃背景层 -->
      <div class="glass-layer" :class="{ 'glass-layer-visible': glassLayerVisible }"></div>
    </div>

    <!-- 右侧登录卡片 -->
    <div class="login-card-container">
      <div 
        class="login-card-wrapper"
        :class="{ 'card-loaded': cardLoaded, 'fade-in': fadeIn }"
      >
        <div class="login-card">
          <!-- 标题（手绘字体风格） -->
          <div class="login-header">
            <h1 class="handwrite-title">校园失物招领系统</h1>
            <p class="sub-title">Lost & Found Platform</p>
          </div>

          <!-- 身份选择标签页 -->
          <div class="role-tabs">
            <div 
              v-for="role in roleOptions" 
              :key="role.value"
              class="role-tab"
              :class="{ 
                'active': form.role === role.value,
                'student-tab': role.value === 1,
                'admin-tab': role.value === 2,
                'system-tab': role.value === 3
              }"
              @click="form.role = role.value"
            >
              <span class="tab-label">{{ role.label }}</span>
            </div>
          </div>

          <!-- 表单 -->
          <div class="login-form">
            <!-- 输入框（手绘边框） -->
            <div class="input-group">
              <span class="input-icon">
                <img :src="currentIdIcon" alt="账号" class="icon-svg" />
              </span>
              <input
                v-model="form.username"
                type="text"
                :placeholder="currentPlaceholder"
                class="handwrite-input"
                @focus="onInputFocus"
                @blur="onInputBlur"
              />
            </div>

            <div class="input-group">
              <span class="input-icon">
                <img src="/login/密码.svg" alt="密码" class="icon-svg" />
              </span>
              <input
                v-model="form.password"
                type="password"
                :placeholder="currentPasswordHint"
                class="handwrite-input"
                @focus="onInputFocus"
                @blur="onInputBlur"
              />
            </div>

            <!-- 记住我（所有身份） -->
            <div class="remember-me">
              <label class="remember-label">
                <input 
                  v-model="rememberMe" 
                  type="checkbox" 
                  class="remember-checkbox" 
                />
                <span class="custom-checkbox"></span>
                <span class="remember-text">记住我</span>
              </label>
              <a v-if="form.role === 1" href="#" class="forgot-password">忘记密码？</a>
            </div>

            <!-- 错误提示（手绘气泡） -->
            <div v-if="errorMsg" class="error-msg bubble">
              <span class="error-icon">⚠️</span>
              {{ errorMsg }}
            </div>

            <!-- 登录按钮（手绘渐变+动效） -->
            <button 
              :disabled="loading" 
              @click="handleLogin"
              class="handwrite-btn"
              :class="{
                'btn-loading': loading,
                'student-btn': form.role === 1,
                'admin-btn': form.role === 2,
                'system-btn': form.role === 3
              }"
            >
              <span v-if="loading" class="loading-spinner">
                <img src="/login/载入.svg" alt="加载中" class="loading-svg" />
              </span>
              <span v-else>{{ currentLoginText }}</span>
            </button>
          </div>

          <!-- 底部说明 -->
          <div class="login-footer">
            <p class="footer-note">
              {{ footerNote }}
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()

/** 表单数据 */
const form = reactive({
  username: '',
  password: '',
  role: 1, // 1: 学生/老师, 2: 失物招领管理员, 3: 系统管理员
})

/** 角色选项 */
const roleOptions = [
  {
    value: 1,
    label: '学生/老师',
    placeholder: '请输入学号 / 工号',
    passwordHint: '请输入密码（初始为身份证后六位）',
    loginText: '登录',
    footerNote: '首次登录请使用身份证后六位作为密码，登录后可修改'
  },
  {
    value: 2,
    label: '失物招领管理员',
    placeholder: '请输入管理员账号',
    passwordHint: '请输入管理员密码',
    loginText: '登录',
    footerNote: '仅限失物招领中心工作人员使用'
  },
  {
    value: 3,
    label: '系统管理员',
    placeholder: '请输入系统管理员账号',
    passwordHint: '请输入系统管理员密码',
    loginText: '登录',
    footerNote: '系统配置与用户管理'
  }
]

/** 计算属性 */
const currentPlaceholder = computed(() => 
  roleOptions.find(r => r.value === form.role)?.placeholder || ''
)

const currentPasswordHint = computed(() => 
  roleOptions.find(r => r.value === form.role)?.passwordHint || ''
)

const currentLoginText = computed(() => 
  roleOptions.find(r => r.value === form.role)?.loginText || '登录'
)

const currentIdIcon = computed(() => '/login/登录.svg')

const footerNote = computed(() => 
  roleOptions.find(r => r.value === form.role)?.footerNote || ''
)

/** 状态 */
const loading = ref(false)
const errorMsg = ref('')
const backgroundLoaded = ref(false)
const cardLoaded = ref(false)
const fadeIn = ref(false)
const isInputFocused = ref(false)
const glassLayerVisible = ref(false)
const rememberMe = ref(false)

/** 页面加载后触发入场动画 */
onMounted(() => {
  // 立即显示毛玻璃层（无延迟）
  glassLayerVisible.value = true
  
  // 背景淡入
  setTimeout(() => {
    backgroundLoaded.value = true
  }, 50)
  
  // 整体淡入
  setTimeout(() => {
    fadeIn.value = true
  }, 150)
  
  // 卡片滑入（但毛玻璃效果已经预先渲染）
  setTimeout(() => {
    cardLoaded.value = true
  }, 200)

  // 尝试读取记住的账号
  loadRememberedAccount()
})

/** 加载记住的账号 */
const loadRememberedAccount = () => {
  const remembered = localStorage.getItem(`rememberedUsername_${form.role}`)
  if (remembered) {
    form.username = remembered
    rememberMe.value = true
  }
}

/** 输入框聚焦处理 */
const onInputFocus = () => {
  isInputFocused.value = true
}

/** 输入框失焦处理 */
const onInputBlur = () => {
  isInputFocused.value = false
}

/** 表单验证 */
const validateForm = () => {
  if (!form.username) {
    errorMsg.value = '请输入账号'
    return false
  }
  
  if (!form.password) {
    errorMsg.value = '请输入密码'
    return false
  }
  
  // 学生/老师账号格式验证（数字）
  if (form.role === 1 && !/^\d+$/.test(form.username)) {
    errorMsg.value = '学号/工号应为数字'
    return false
  }
  
  return true
}

/** 角色到登录类型的映射 */
const roleToLoginType = (role: number) => {
  switch (role) {
    case 1:
      return 'user'
    case 2:
      return 'item_admin'
    case 3:
      return 'system_admin'
    default:
      return 'user'
  }
}

/** 登录处理 */
const handleLogin = async () => {
  if (!validateForm()) {
    return
  }

  loading.value = true
  errorMsg.value = ''

  try {
    const res = await axios.post(
      '/api/user/login',
      {
        username: form.username,
        password: form.password,
        loginType: roleToLoginType(form.role)
      },
      {
        withCredentials: true   
      }
    )

    if (res.data.code !== 0) {
      errorMsg.value = res.data.msg || '登录失败'
      return
    }

    const user = res.data.data

    // 保存用户信息
    sessionStorage.setItem('userId', user.id)
    sessionStorage.setItem('realName', user.realName)
    sessionStorage.setItem('role', user.role)
    sessionStorage.setItem('firstLogin', user.firstLogin)
    sessionStorage.setItem('loginTime', new Date().toISOString())
    
    // 记住我功能 - 所有角色都支持
    if (rememberMe.value) {
      localStorage.setItem(`rememberedUsername_${form.role}`, form.username)
    } else {
      localStorage.removeItem(`rememberedUsername_${form.role}`)
    }

    // 首次登录强制修改密码
    if (user.firstLogin) {
      router.push('/force-change-password')
      return
    }

    // 根据角色跳转到默认页面
    if (user.role === 1 || user.role === 2) {
      router.push('/home')
    } else if (user.role === 3) {
      router.push('/item-admin/notices')
    } else if (user.role === 4) {
      router.push('/system-admin/dashboard')
    } else {
      router.push('/home')
    }
  } catch (err: any) {
    if (err.response?.status === 401) {
      errorMsg.value = '账号或密码错误'
    } else if (err.response?.status === 403) {
      errorMsg.value = '您没有该角色的访问权限'
    } else {
      errorMsg.value = '无法连接服务器，请检查网络'
    }
  } finally {
    loading.value = false
  }
}

/** 监听角色变化 */
watch(() => form.role, (newRole) => {
  // 清除表单和错误信息
  form.username = ''
  form.password = ''
  errorMsg.value = ''
  
  // 加载对应角色的记住的账号
  const remembered = localStorage.getItem(`rememberedUsername_${newRole}`)
  if (remembered) {
    form.username = remembered
    rememberMe.value = true
  } else {
    rememberMe.value = false
  }
})
</script>

<style scoped>
/* 基础布局 */
.login-page {
  width: 100vw;
  height: 100vh;
  position: relative;
  overflow: hidden;
  background: #fce38a;
}

/* 背景图片容器 */
.background-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
  overflow: hidden;
}

.background-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  opacity: 0;
  transform: scale(1.1);
  transition: all 1.2s ease-out;
}

.background-loaded {
  opacity: 1;
  transform: scale(1);
}

/* 预渲染的毛玻璃层 */
.glass-layer {
  position: absolute;
  top: 0;
  right: 0;
  width: 50%;
  height: 100%;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(25px);
  -webkit-backdrop-filter: blur(25px);
  border-left: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 
    -15px 0 40px rgba(0, 0, 0, 0.15),
    inset 1px 0 0 rgba(255, 255, 255, 0.1);
  opacity: 0;
  transform: translateX(100px);
  transition: all 0.3s ease-out;
  pointer-events: none;
  will-change: opacity, transform;
}

.glass-layer-visible {
  opacity: 1;
  transform: translateX(0);
}

/* 登录卡片容器 */
.login-card-container {
  position: absolute;
  top: 0;
  right: 0;
  width: 50%;
  height: 100vh;
  z-index: 2;
  overflow: hidden;
}

.login-card-wrapper {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  transform: translateX(100px);
  transition: all 0.9s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  will-change: opacity, transform;
  display: flex;
  align-items: center;
  justify-content: center;
}

.fade-in {
  opacity: 1;
}

.card-loaded {
  transform: translateX(0);
  opacity: 1;
}

/* 登录卡片 */
.login-card {
  width: 100%;
  height: 100%;
  padding: 60px 70px;
  background: transparent;
  border-radius: 0;
  transition: all 0.4s ease;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

/* 标题区域 */
.login-header {
  text-align: center;
  margin-bottom: 30px;
  position: relative;
}

.handwrite-title {
  font-size: 44px;
  margin: 0 0 15px 0;
  color: #a67c52;
  font-weight: 600;
  font-family: "Comic Sans MS", "Marker Felt", cursive;
  position: relative;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
}

.handwrite-title::after {
  content: "";
  position: absolute;
  bottom: -15px;
  left: 30%;
  width: 40%;
  height: 4px;
  background: linear-gradient(to right, #f38181, #f77d5f);
  border-radius: 2px;
  opacity: 0.8;
}

.sub-title {
  margin-top: 20px;
  font-size: 18px;
  color: #a67c52;
  font-family: "Comic Sans MS", cursive;
  letter-spacing: 2px;
}

/* 角色标签页 */
.role-tabs {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-bottom: 40px;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 8px;
  border: 2px solid rgba(166, 124, 82, 0.2);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.role-tab {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 24px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: "Comic Sans MS", cursive;
  color: rgba(166, 124, 82, 0.8);
  border: 2px solid transparent;
  position: relative;
  overflow: hidden;
}

.role-tab:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
}

.role-tab.active {
  color: white;
  border-color: transparent;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.role-tab.active::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(to right, #f38181, #f77d5f);
  z-index: -1;
  border-radius: 10px;
}

/* 不同角色的标签样式 */
.student-tab.active::before {
  background: linear-gradient(to right, #f38181, #f77d5f);
}

.admin-tab.active::before {
  background: linear-gradient(to right, #f38181, #f77d5f);
}

.system-tab.active::before {
  background: linear-gradient(to right, #f38181, #f77d5f);
}

.tab-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
}



.tab-label {
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 1px;
}

/* 表单区域 */
.login-form {
  width: 100%;
  max-width: 500px;
}

/* 表单提示 */
.form-hint {
  text-align: center;
  margin-bottom: 25px;
}



/* 输入框组 */
.input-group {
  position: relative;
  margin-bottom: 25px;
}

.input-icon {
  position: absolute;
  left: 20px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 24px;
  color: rgba(166, 124, 82, 0.8);
  z-index: 2;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon-svg {
  width: 24px;
  height: 24px;
  object-fit: contain;
  filter: brightness(0.8);
}

/* 输入框 */
.handwrite-input {
  width: 83%;
  height: 60px;
  padding: 0 20px 0 60px;
  border-radius: 12px;
  border: 2px solid rgba(166, 124, 82, 0.4);
  font-size: 18px;
  outline: none;
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  transition: all 0.3s ease;
  font-family: "Comic Sans MS", cursive;
  color: #a67c52;
  font-weight: 500;
  transform: translateZ(0);
  -webkit-transform: translateZ(0);
  will-change: background, backdrop-filter, transform;
}

.handwrite-input::placeholder {
  color: rgba(166, 124, 82, 0.6);
  font-family: "Comic Sans MS", cursive;
}

.handwrite-input:focus {
  background: rgba(255, 255, 255, 0.35);
  backdrop-filter: blur(15px);
  -webkit-backdrop-filter: blur(15px);
  border-color: rgba(243,129,129,1.00);
  box-shadow: 
    0 0 0 3px rgba(102, 126, 234, 0.15),
    0 8px 20px rgba(0, 0, 0, 0.1);
  transform: translateY(-1px) translateZ(0);
}

.handwrite-input:focus + .input-icon {
  color: #f77d5f;
  transform: translateY(-50%) scale(1.1);
}

/* 验证码输入组 */
.captcha-group {
  margin-bottom: 15px;
}

.captcha-input {
  width: 65%;
  margin-right: 15px;
}

.captcha-hint {
  position: absolute;
  right: 20px;
  top: 50%;
  transform: translateY(-50%);
  padding: 10px 15px;
  background: rgba(255, 255, 255, 0.3);
  backdrop-filter: blur(10px);
  border-radius: 10px;
  border: 1px dashed rgba(166, 124, 82, 0.4);
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 10px;
  font-family: "Comic Sans MS", cursive;
  color: #a67c52;
  font-weight: 600;
  letter-spacing: 2px;
  font-size: 18px;
}

.captcha-hint:hover {
  background: rgba(255, 255, 255, 0.4);
  transform: translateY(-50%) scale(1.05);
}

.refresh-icon {
  font-size: 16px;
  opacity: 0.7;
  transition: transform 0.3s ease;
}

.captcha-hint:hover .refresh-icon {
  transform: rotate(180deg);
}

/* 记住我和忘记密码 */
.remember-me {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
  padding: 0 10px;
}

.remember-label {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  font-family: "Comic Sans MS", cursive;
  color: #a67c52;
}

.remember-checkbox {
  display: none;
}

.custom-checkbox {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(166, 124, 82, 0.6);
  border-radius: 6px;
  position: relative;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.2);
}

.remember-checkbox:checked + .custom-checkbox {
  background: #f77d5f;
  border-color: #f77d5f;
}

.remember-checkbox:checked + .custom-checkbox::after {
  content: '✓';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: white;
  font-size: 14px;
  font-weight: bold;
}

.remember-text {
  font-size: 15px;
}

.forgot-password {
  color: #f77d5f;
  text-decoration: none;
  font-family: "Comic Sans MS", cursive;
  font-size: 15px;
  position: relative;
}

.forgot-password::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 0;
  height: 1px;
  background: #f77d5f;
  transition: width 0.3s ease;
}

.forgot-password:hover::after {
  width: 100%;
}

/* 错误提示 */
.error-msg {
  color: #d35400;
  font-size: 16px;
  margin: 20px 0;
  padding: 14px 18px;
  background: rgba(255, 243, 224, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  border: 1px solid rgba(245, 183, 142, 0.6);
  font-family: "Comic Sans MS", cursive;
  position: relative;
  animation: shake 0.4s ease;
  transform: translateZ(0);
  -webkit-transform: translateZ(0);
  will-change: transform;
  display: flex;
  align-items: center;
  gap: 10px;
}

.error-icon {
  font-size: 18px;
}

@keyframes shake {
  0%, 100% { transform: translateX(0) translateZ(0); }
  25% { transform: translateX(-5px) translateZ(0); }
  75% { transform: translateX(5px) translateZ(0); }
}

/* 登录按钮 */
.handwrite-btn {
  width: 100%;
  height: 62px;
  border: none;
  border-radius: 12px;
  color: white;
  font-size: 20px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: "Comic Sans MS", cursive;
  position: relative;
  overflow: hidden;
  margin-top: 10px;
  letter-spacing: 1px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  transform: translateZ(0);
  -webkit-transform: translateZ(0);
  will-change: transform, box-shadow;
}

/* 不同角色的按钮颜色 */
.student-btn {
  background: linear-gradient(to right, #f38181, #f77d5f);
}

.admin-btn {
  background: linear-gradient(to right, #f38181, #f77d5f);
}

.system-btn {
  background: linear-gradient(to right, #f38181, #f77d5f);
}

.handwrite-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, 
    transparent, 
    rgba(255, 255, 255, 0.2), 
    transparent);
  transition: left 0.6s ease;
}

.handwrite-btn:hover {
  transform: translateY(-3px) translateZ(0);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
}

.handwrite-btn:hover::before {
  left: 100%;
}

.handwrite-btn:active {
  transform: translateY(-1px) translateZ(0);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.handwrite-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.btn-loading .loading-spinner {
  display: flex;
  align-items: center;
  justify-content: center;
  animation: spin 1.2s linear infinite;
}

.loading-svg {
  width: 24px;
  height: 24px;
  object-fit: contain;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 登录页脚 */
.login-footer {
  margin-top: 30px;
  text-align: center;
}

.footer-note {
  font-family: "Comic Sans MS", cursive;
  color: rgba(166, 124, 82, 0.8);
  font-size: 14px;
  line-height: 1.6;
}

.register-link {
  color: #4facfe;
  text-decoration: none;
  margin-left: 5px;
  font-weight: 600;
  position: relative;
}

.register-link::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 0;
  height: 1px;
  background: #4facfe;
  transition: width 0.3s ease;
}

.register-link:hover::after {
  width: 100%;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .login-card-container {
    width: 55%;
  }
  
  .glass-layer {
    width: 55%;
  }
}

@media (max-width: 768px) {
  .background-container {
    width: 100%;
  }
  
  .glass-layer {
    width: 100%;
    border-left: none;
    box-shadow: none;
  }
  
  .login-card-container {
    width: 100%;
    padding: 20px;
  }
  
  .login-card-wrapper {
    max-width: 400px;
  }
  
  .login-card {
    padding: 40px 30px;
  }
  
  .handwrite-title {
    font-size: 28px;
  }
  
  .sub-title {
    font-size: 14px;
  }
  
  .role-tabs {
    flex-direction: column;
    gap: 10px;
  }
  
  .role-tab {
    justify-content: center;
  }
  
  .handwrite-input {
    height: 52px;
    font-size: 16px;
  }
  
  .handwrite-btn {
    height: 56px;
    font-size: 18px;
  }
}
</style>