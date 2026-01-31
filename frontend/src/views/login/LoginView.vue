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

          <!-- 表单 -->
          <div class="login-form">
            <!-- 输入框（手绘边框） -->
            <div class="input-group">
              <span class="input-icon">📚</span>
              <input
                v-model="form.username"
                type="text"
                placeholder="请输入学号 / 工号"
                class="handwrite-input"
                @focus="onInputFocus"
                @blur="onInputBlur"
              />
            </div>

            <div class="input-group">
              <span class="input-icon">🔑</span>
              <input
                v-model="form.password"
                type="password"
                placeholder="请输入密码（初始为身份证后六位）"
                class="handwrite-input"
                @focus="onInputFocus"
                @blur="onInputBlur"
              />
            </div>

            <!-- 错误提示（手绘气泡） -->
            <div v-if="errorMsg" class="error-msg bubble">
              {{ errorMsg }}
            </div>

            <!-- 登录按钮（手绘渐变+动效） -->
            <button 
              :disabled="loading" 
              @click="handleLogin"
              class="handwrite-btn"
              :class="{ 'btn-loading': loading }"
            >
              <span v-if="loading" class="loading-spinner">⏳</span>
              <span v-else>登录</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()

/** 表单数据 */
const form = reactive({
  username: '',
  password: ''
})

/** 状态 */
const loading = ref(false)
const errorMsg = ref('')
const backgroundLoaded = ref(false)
const cardLoaded = ref(false)
const fadeIn = ref(false)
const isInputFocused = ref(false)
const glassLayerVisible = ref(false)

// 页面加载后触发入场动画
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
})

/** 输入框聚焦处理 */
const onInputFocus = () => {
  isInputFocused.value = true
}

/** 输入框失焦处理 */
const onInputBlur = () => {
  isInputFocused.value = false
}

/** 登录处理 */
const handleLogin = async () => {
  if (!form.username || !form.password) {
    errorMsg.value = '请输入学号/工号和密码'
    return
  }

  loading.value = true
  errorMsg.value = ''

  try {
    const res = await axios.post('/api/user/login', {
      username: form.username,
      password: form.password
    })

    if (res.data.code !== 0) {
      errorMsg.value = res.data.msg || '登录失败'
      return
    }

    const user = res.data.data

    // 保存用户信息
    localStorage.setItem('userId', user.id)
    localStorage.setItem('realName', user.realName)
    localStorage.setItem('role', user.role)

    // 根据角色跳转
    if (user.role === 1 || user.role === 2) {
      router.push('/home')
    } else if (user.role === 3) {
      router.push('/admin/dashboard')
    } else if (user.role === 4) {
      router.push('/system/dashboard')
    } else {
      router.push('/home')
    }
  } catch (err) {
    errorMsg.value = '无法连接服务器'
  } finally {
    loading.value = false
  }
}
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

/* 预渲染的毛玻璃层 - 解决backdrop-filter延迟问题 */
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

/* 优化：硬件加速 */
.glass-layer {
  transform: translateZ(0);
  -webkit-transform: translateZ(0);
  backface-visibility: hidden;
  -webkit-backface-visibility: hidden;
  perspective: 1000;
  -webkit-perspective: 1000;
}

/* 右侧登录卡片容器 - 占据右侧50%全屏 */
.login-card-container {
  position: absolute;
  top: 0;
  right: 0;
  width: 50%;
  height: 100vh;
  z-index: 2;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.login-card-wrapper {
  width: 100%;
  height: 100%;
  opacity: 0;
  transform: translateX(100px);
  transition: all 0.9s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  will-change: opacity, transform;
}

/* 页面整体淡入效果 */
.fade-in {
  opacity: 1;
}

/* 卡片滑入效果 */
.card-loaded {
  transform: translateX(0);
  opacity: 1;
}

/* 登录卡片 - 透明背景，毛玻璃效果由glass-layer提供 */
.login-card {
  width: 100%;
  height: 100%;
  padding: 80px 70px;
  background: transparent;
  border-radius: 0;
  transition: all 0.4s ease;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

/* 移除卡片的毛玻璃相关样式，改为透明背景 */
.login-card:hover {
  background: transparent;
  box-shadow: none;
  transform: translateY(-2px);
}

/* 移除卡片的流光效果 */
.login-card::before {
  content: none;
}

/* 标题区域 - 放大 */
.login-header {
  text-align: center;
  margin-bottom: 50px;
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
  background: linear-gradient(90deg, #667eea, #764ba2);
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

/* 表单区域 */
.login-form {
  width: 100%;
  max-width: 500px;
}

/* 输入框组 - 放大 */
.input-group {
  position: relative;
  margin-bottom: 35px;
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
}

/* 输入框 - 放大 */
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
  /* 硬件加速优化 */
  transform: translateZ(0);
  -webkit-transform: translateZ(0);
  will-change: background, backdrop-filter, transform;
}

.handwrite-input::placeholder {
  color: rgba(166, 124, 82, 0.6);
  font-family: "Comic Sans MS", cursive;
}

/* 输入框聚焦效果 - 毛玻璃透明度变化 */
.handwrite-input:focus {
  background: rgba(255, 255, 255, 0.35);
  backdrop-filter: blur(15px);
  -webkit-backdrop-filter: blur(15px);
  border-color: rgba(102, 126, 234, 0.7);
  box-shadow: 
    0 0 0 3px rgba(102, 126, 234, 0.15),
    0 8px 20px rgba(0, 0, 0, 0.1);
  transform: translateY(-1px) translateZ(0);
}

.handwrite-input:focus + .input-icon {
  color: #667eea;
  transform: translateY(-50%) scale(1.1);
}

/* 错误提示 - 放大 */
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
  /* 硬件加速 */
  transform: translateZ(0);
  -webkit-transform: translateZ(0);
  will-change: transform;
}

@keyframes shake {
  0%, 100% { transform: translateX(0) translateZ(0); }
  25% { transform: translateX(-5px) translateZ(0); }
  75% { transform: translateX(5px) translateZ(0); }
}

/* 登录按钮 - 放大 */
.handwrite-btn {
  width: 100%;
  height: 62px;
  border: none;
  border-radius: 12px;
  background: linear-gradient(to right, #f38181, #f77d5f);
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
  box-shadow: 0 4px 15px rgba(247, 125, 95, 0.3);
  /* 硬件加速 */
  transform: translateZ(0);
  -webkit-transform: translateZ(0);
  will-change: transform, box-shadow;
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
  box-shadow: 0 8px 25px rgba(247, 125, 95, 0.4);
  background: linear-gradient(to right, #f77d5f, #f38181);
}

.handwrite-btn:hover::before {
  left: 100%;
}

.handwrite-btn:active {
  transform: translateY(-1px) translateZ(0);
  box-shadow: 0 4px 15px rgba(247, 125, 95, 0.3);
}

.handwrite-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.btn-loading .loading-spinner {
  display: inline-block;
  animation: spin 1.2s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
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