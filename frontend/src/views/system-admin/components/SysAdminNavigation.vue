<!-- src/views/system-admin/components/SysAdminNavigation.vue -->
<template>
  <!-- 左侧导航栏 -->
  <aside class="left-nav">
    <!-- 用户信息区域 -->
    <div class="user-info-container">
      <div class="user-avatar-container">
        <img class="user-avatar" src="/home/avatar.png" />
        <div class="user-avatar-border"></div>
      </div>
      <div class="user-text">
        <div class="user-nickname">{{ user.realName }}</div>
        <div class="user-subtitle">{{ subtitle }}</div>
      </div>
    </div>

    <!-- 左侧上半区：核心导航 -->
    <div class="nav-top-group">
      <button 
        v-for="nav in navItems" 
        :key="nav.name"
        class="left-nav-btn"
        :class="{ active: isActive(nav) }"
        @click="nav.handler"
      >
        <span class="nav-icon">
          <img :src="nav.icon" :alt="nav.name" class="nav-svg" />
        </span>
        <span class="nav-text">{{ nav.name }}</span>
        <!-- 消息红点 -->
        <span v-if="nav.name === '投诉处理' && pendingComplaints > 0" class="nav-badge">
          {{ pendingComplaints > 99 ? '99+' : pendingComplaints }}
        </span>
      </button>
    </div>

    <!-- 左侧中间：自定义内容插槽 -->
    <div v-if="hasCustomContent" class="left-notice-card bubble">
      <slot name="custom-content"></slot>
    </div>

    <!-- 左侧下半区：操作按钮 -->
    <div class="nav-bottom-group">
      <button 
        class="left-action-btn logout-btn"
        @click="handleLogout"
      >
        <span class="btn-text">退出登录</span>
      </button>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

interface NavItem {
  name: string
  icon: string
  active?: boolean
  handler: () => void
}

interface Props {
  subtitle?: string
  activeNav?: string
  pendingComplaints?: number
  customContent?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  subtitle: '超级管理员',
  activeNav: '',
  pendingComplaints: 0,
  customContent: false
})

const emit = defineEmits<{
  logout: []
  navClick: [navName: string]
}>()

const router = useRouter()
const user = ref({
  id: 0,
  username: '',
  realName: '加载中...',
  phone: '',
  role: 0,
  status: 0
})

// 计算是否有自定义内容
const hasCustomContent = computed(() => props.customContent)

// 导航项配置 - 系统管理员专用
const navItems = ref<NavItem[]>([
  {
    name: '全局总览',
    icon: '/home/发现.svg',
    handler: () => router.push('/system-admin/dashboard')
  },
  {
    name: '系统配置',
    icon: '/home/设置.svg',
    handler: () => router.push('/system-admin/config')
  },
  {
    name: '账号管理',
    icon: '/home/我的.svg',
    handler: () => router.push('/system-admin/accounts')
  },
  {
    name: '公告管理',
    icon: '/home/消息.svg',
    handler: () => router.push('/system-admin/notices')
  },
  {
    name: '数据管理',
    icon: '/home/发布.svg',
    handler: () => router.push('/system-admin/data')
  },

])

// 判断导航项是否激活
const isActive = (nav: NavItem) => {
  if (props.activeNav) {
    return nav.name === props.activeNav
  }
  return nav.active || false
}

// 退出登录处理
const handleLogout = async () => {
  try {
    const userId = user.value.id
    if (userId) {
      await axios.post('/api/user/logout', { userId })
    }
  } catch (error) {
    console.error('退出登录失败:', error)
  } finally {
    localStorage.clear()
    sessionStorage.clear()
    emit('logout')
    router.push('/login')
  }
}

// 加载用户信息
const loadUser = async () => {
  try {
    const res = await axios.get('/api/user/info')
    if (res.data.code === 0) {
      user.value = res.data.data
    }
  } catch (error) {
    console.error('加载用户信息失败:', error)
    // 模拟数据用于演示
    user.value = {
      id: 1,
      username: 'admin',
      realName: '系统管理员',
      phone: '13800000000',
      role: 5, // 超级管理员角色
      status: 1
    }
  }
}

onMounted(() => {
  loadUser()
})
</script>

<style scoped>
/* 左侧导航栏样式 */
.left-nav {
  width: 288px;
  height: 100vh;
  position: fixed;
  top: 0;
  left: 0;
  background: transparent;
  padding: 24px;
  display: flex;
  flex-direction: column;
  z-index: 1000;
  box-sizing: border-box;
}

/* 用户信息区域 */
.user-info-container {
  border-radius: 12.8px;
  padding: 16px;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar-container {
  position: relative;
  width: 48px;
  height: 48px;
}

.user-avatar {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
}

.user-avatar-border {
  position: absolute;
  top: -4px;
  left: -4px;
  right: -4px;
  bottom: -4px;
  border: 2px solid rgba(243, 129, 129, 0.5);
  border-radius: 50%;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 0.8; }
}

.user-text {
  display: flex;
  flex-direction: column;
}

.user-nickname {
  font-family: "Comic Sans MS", "Marker Felt", cursive;
  font-size: 20px;
  font-weight: 600;
  color: #a67c52;
  margin-bottom: 6.4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 192px;
}

.user-subtitle {
  font-family: "Comic Sans MS", cursive;
  font-size: 17.6px;
  color: rgba(166, 124, 82, 0.7);
}

/* 左侧上半区：核心导航组 */
.nav-top-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 8px;
}

/* 左侧导航按钮样式 */
.left-nav-btn {
  background: transparent;
  border: none;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 16px;
  cursor: pointer;
  padding: 14.4px 10px;
  border-radius: 12.8px;
  transition: all 0.3s ease;
  font-family: "Comic Sans MS", cursive;
  color: #a67c52;
  font-size: 16px;
  font-weight: 500;
  width: 100%;
  text-align: left;
  position: relative;
}

.left-nav-btn:hover {
  background: rgba(255, 255, 255, 0.15);
  transform: translateX(5px);
}

.left-nav-btn.active {
  background: rgba(243, 129, 129, 0.15);
  font-weight: 600;
}

.nav-icon {
  font-size: 25.6px;
  min-width: 32px;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
}

.nav-svg {
  width: 25.6px;
  height: 25.6px;
  object-fit: contain;
  filter: brightness(0.8);
}

.nav-text {
  font-size: 20px;
}

/* 消息红点 */
.nav-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  background: #ff6b6b;
  color: white;
  border-radius: 10px;
  padding: 2px 6px;
  font-family: "Comic Sans MS", cursive;
  font-size: 10px;
  font-weight: 600;
  min-width: 18px;
  height: 16px;
  line-height: 16px;
  text-align: center;
  box-shadow: 0 2px 6px rgba(255, 107, 107, 0.3);
  animation: pulse-badge 2s infinite;
  z-index: 1;
}

@keyframes pulse-badge {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

/* 左侧中间：公告栏/自定义内容 */
.left-notice-card {
  background: rgba(255, 255, 255, 0.15);
  border-radius: 14.4px;
  padding: 16px;
  margin: 15px 0;
  border: 1.6px solid rgba(166, 124, 82, 0.2);
  display: flex;
  flex-direction: column;
  width: 85%;
  max-height: 300px;
  min-height: 96px;
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: rgba(166, 124, 82, 0.15) transparent;
  box-sizing: border-box;
}

.left-notice-card .notice-title {
  font-family: "Comic Sans MS", cursive;
  font-size: 18px;
  color: #a67c52;
  margin-bottom: 15px;
  font-weight: 600;
  text-align: center;
  flex-shrink: 0;
}

.left-notice-card .notice-desc {
  font-family: "Comic Sans MS", cursive;
  font-size: 16px;
  color: rgba(166, 124, 82, 0.8);
  line-height: 1.5;
  text-align: center;
  margin-bottom: 20px;
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding-right: 5px;
  word-wrap: break-word;
}

.left-notice-card .notice-time {
  font-family: "Comic Sans MS", cursive;
  font-size: 12px;
  color: rgba(166, 124, 82, 0.6);
  text-align: right;
  flex-shrink: 0;
  margin-top: 10px;
}

/* 左侧下半区：操作按钮组 */
.nav-bottom-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: auto;
}

/* 左侧操作按钮样式 */
.left-action-btn {
  height: 54.4px;
  padding: 0 25.6px;
  border-radius: 12.8px;
  font-family: "Comic Sans MS", cursive;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  border: 1.6px solid transparent;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
  color: white;
  width: 100%;
}

.left-action-btn:hover {
  transform: translateX(5px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
}

.logout-btn {
  background: linear-gradient(to right, #f38181, #f77d5f);
  width: 75%;
}

/* 响应式设计：移动端（768px以下） */
@media (max-width: 768px) {
  .left-nav {
    width: 100%;
    height: auto;
    position: fixed;
    bottom: 0;
    left: 0;
    top: auto;
    border-right: none;
    border-top: 2px solid rgba(166, 124, 82, 0.2);
    padding: 10px 15px;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    gap: 0;
    z-index: 100;
  }

  /* 移动端隐藏用户信息、公告栏 */
  .user-info-container,
  .left-notice-card {
    display: none;
  }

  /* 导航组调整为横向 */
  .nav-top-group {
    flex-direction: row;
    flex: 1;
    margin-top: 0;
    justify-content: space-around;
  }

  .left-nav-btn {
    flex-direction: column;
    padding: 10px 5px;
    gap: 4px;
    width: auto;
    min-width: 60px;
  }

  .left-nav-btn .nav-icon {
    font-size: 22px;
    min-width: auto;
  }
  
  .left-nav-btn .nav-svg {
    width: 22px;
    height: 22px;
  }

  .left-nav-btn .nav-text {
    font-size: 10px;
    text-align: center;
  }

  /* 底部操作按钮组 */
  .nav-bottom-group {
    flex-direction: row;
    margin-top: 0;
    margin-left: 10px;
  }

  .left-action-btn {
    height: 40px;
    padding: 0 15px;
    font-size: 14px;
    min-width: 80px;
  }
}

/* 平板端适配（769px-1024px） */
@media (min-width: 769px) and (max-width: 1024px) {
  .left-nav {
    width: 300px;
  }
  
  .user-nickname {
    max-width: 120px;
  }
}
</style>