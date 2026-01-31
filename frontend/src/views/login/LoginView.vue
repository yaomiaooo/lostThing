<template>
  <div class="login-page">
    <!-- 左右分栏布局 -->
    <div class="login-container">
      <!-- 左侧图片区域 -->
      <div class="login-left">
        <div class="image-content">
          <img src="/login/left_image.png" alt="校园失物招领" class="left-image" />
          <div class="image-overlay">
            <h2 class="image-title">校园失物招领系统</h2>
            <p class="image-subtitle">让遗失的物品找到回家的路</p>
          </div>
        </div>
      </div>

      <!-- 右侧登录区域 -->
      <div class="login-right">
        <!-- 登录卡片 -->
        <div class="login-card" :class="{ 'login-card-animate': isLoaded }">
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
              />
            </div>

            <div class="input-group">
              <span class="input-icon">🔑</span>
              <input
                v-model="form.password"
                type="password"
                placeholder="请输入密码（初始为身份证后六位）"
                class="handwrite-input"
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
const isLoaded = ref(false) // 控制卡片入场动画

// 页面加载后触发入场动画
onMounted(() => {
  setTimeout(() => {
    isLoaded.value = true
  }, 300)
})

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
/* 基础布局：使用暖黄色渐变背景 */
.login-page {
  width: 100vw;
  height: 100vh;
  background: #fce38a;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}



/* 左右分栏布局 */
.login-container {
  width: 90%;
  max-width: 1200px;
  height: 80vh;
  display: flex;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  overflow: hidden;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.3);
}

/* 左侧图片区域 */
.login-left {
  flex: 1.2;
  position: relative;
  overflow: hidden;
}

.image-content {
  width: 100%;
  height: 100%;
  position: relative;
}

.left-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: brightness(0.8) contrast(1.1);
  transition: transform 0.5s ease;
}

.image-content:hover .left-image {
  transform: scale(1.05);
}

.image-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 40px;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.8));
  color: white;
}

.image-title {
  font-size: 32px;
  margin: 0 0 10px 0;
  font-weight: bold;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
}

.image-subtitle {
  font-size: 16px;
  margin: 0;
  opacity: 0.9;
}

/* 右侧登录区域 */
.login-right {
  flex: 0.8;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  height: 100vh;
}

/* 登录卡片：玻璃拟态效果+高级动画，铺满右侧区域 */
.login-card {
  width: 100%;
  height: 100%;
  max-width: none;
  padding: 60px 40px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(30px);
  border-radius: 0;
  border: none;
  box-shadow: 
    0 0 0 rgba(0, 0, 0, 0),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  transform: translateX(50px);
  opacity: 0;
  transition: all 0.8s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.login-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
  transition: left 0.8s;
}

.login-card:hover::before {
  left: 100%;
}

.login-card-animate {
  transform: translateX(0);
  opacity: 1;
}

/* 标题：简洁现代风格 */
.login-header {
  text-align: center;
  margin-bottom: 32px;
  position: relative;
}

.handwrite-title {
  font-size: 28px;
  margin: 0;
  color: #a67c52;
  font-weight: 600;
   font-family: "Comic Sans MS", "Marker Felt", cursive; /* 手绘感字体 */
  position: relative;
}

.handwrite-title::after {
  content: "";
  position: absolute;
  bottom: -8px;
  left: 25%;
  width: 50%;
  height: 3px;
  background: linear-gradient(90deg, #667eea, #764ba2);
  border-radius: 2px;
}

.sub-title {
  margin-top: 12px;
  font-size: 14px;
  color: #a67c52;
  font-family: "Comic Sans MS", cursive;
}

/* 输入框：现代简约风格 */
.input-group {
  position: relative;
  margin-bottom: 24px;
}

.input-icon {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 18px;
  color: rgba(255, 255, 255, 0.7);
  z-index: 2;
  transition: all 0.3s;
}

.handwrite-input {
  width: 100%;
  height: 48px;
  padding: 0 20px 0 50px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  font-size: 15px;
  outline: none;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(10px);
  transition: all 0.3s;
  font-family: system-ui, -apple-system, sans-serif;
  color: #fff;
}

.handwrite-input::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.handwrite-input:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
  background: rgba(255, 255, 255, 0.12);
}

.handwrite-input:focus + .input-icon {
  color: #667eea;
  transform: translateY(-50%) scale(1.1);
}

/* 错误提示：手绘气泡 */
.error-msg {
  color: #d35400;
  font-size: 13px;
  margin-bottom: 12px;
  padding: 8px 12px;
  background: #fff3e0;
  border-radius: 12px;
  border: 1px solid #f5b78e;
  font-family: "Comic Sans MS", cursive;
}

.bubble::after {
  content: "";
  position: absolute;
  bottom: -8px;
  left: 20px;
  width: 16px;
  height: 16px;
  background: #fff3e0;
  border: 1px solid #f5b78e;
  border-right: none;
  border-top: none;
  transform: rotate(45deg);
}

/* 登录按钮：现代渐变风格 */
.handwrite-btn {
  width: 100%;
  height: 48px;
  border: none;
  border-radius: 10px;
  background: linear-gradient(to right, #f38181, #f77d5f);
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: system-ui, -apple-system, sans-serif;
  position: relative;
  overflow: hidden;
}

.handwrite-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s;
}

.handwrite-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
}

.handwrite-btn:hover::before {
  left: 100%;
}

.handwrite-btn:active {
  transform: translateY(0);
}

.handwrite-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.btn-loading .loading-spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>