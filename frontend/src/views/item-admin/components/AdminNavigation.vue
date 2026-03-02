<!-- src/views/item-admin/components/AdminNavigation.vue -->
<template>
  <!-- 左侧导航栏 - 添加唯一的key确保组件正确识别 -->
  <aside class="left-nav" :key="navKey">
    <!-- 管理员信息区域 -->
    <div class="user-info-container">
      <div class="user-avatar-container">
        <img class="user-avatar" src="/home/avatar.png" />
        <div class="user-avatar-border"></div>
      </div>
      <div class="user-text">
        <div class="user-nickname">{{ user.realName }}</div>
        <div class="user-role-badge">失物招领管理员</div>
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
        @click="handleNavClick(nav)"
      >
        <span class="nav-icon">
          <img :src="nav.icon" :alt="nav.name" class="nav-svg" />
        </span>
        <span class="nav-text">{{ nav.name }}</span>
        <!-- 待审核数量红点 -->
        <span v-if="nav.name === '待审核' && pendingCount > 0" class="nav-badge">
          {{ pendingCount > 99 ? '99+' : pendingCount }}
        </span>
      </button>
    </div>

    <!-- 左侧中间：快捷统计卡片（自定义内容插槽） -->
    <div v-if="showStatsCard" class="left-notice-card bubble">
      <div class="stats-content">
        <div class="stats-title">📊 今日工作概览</div>
        <div class="stat-item">
          <span class="stat-label">待审核：</span>
          <span class="stat-value pending">{{ stats.pending }}</span>
        </div>
      </div>
      <div class="stats-time">更新时间：{{ updateTime }}</div>
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
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'

interface NavItem {
  name: string
  icon: string
  path: string
  handler: () => void
}

interface Props {
  subtitle?: string
  activeNav?: string
  showStatsCard?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  subtitle: '欢迎回来^_^',
  activeNav: '',
  showStatsCard: true
})

const emit = defineEmits<{
  logout: []
}>()

const router = useRouter()
const route = useRoute()

/* ================= 唯一标识 ================= */
// 使用时间戳+随机数生成唯一key，防止组件复用导致重影
const navKey = ref(`admin-nav-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`)

/* ================= 用户信息 ================= */
const user = ref({
  id: 0,
  username: '',
  realName: '加载中...',
  phone: '',
  role: 3, // 失物招领管理员固定为3
  status: 0
})

/* ================= 统计数据 ================= */
const pendingCount = ref(0)
const stats = ref({
  pending: 0
})
const updateTime = ref('')

/* ================= 导航项配置 ================= */
const navItems = ref<NavItem[]>([
  {
    name: '通知公告',
    icon: '/home/消息.svg',
    path: '/item-admin/notices',
    handler: () => router.push('/item-admin/notices')
  },
  {
    name: '待审核',
    icon: '/home/发现.svg',
    path: '/item-admin/pending',
    handler: () => router.push('/item-admin/pending')
  },
  {
    name: '物品管理',
    icon: '/home/我的.svg',
    path: '/item-admin/items',
    handler: () => router.push('/item-admin/items')
  },
  {
    name: '历史查询',
    icon: '/home/设置.svg',
    path: '/item-admin/history',
    handler: () => router.push('/item-admin/history')
  }
])

/* ================= 判断导航项是否激活 ================= */
const isActive = (nav: NavItem) => {
  if (props.activeNav) {
    return nav.name === props.activeNav
  }
  return route.path === nav.path
}

/* ================= 导航点击处理 ================= */
const handleNavClick = (nav: NavItem) => {
  // 如果已经在当前页面，不执行跳转（防止重复渲染）
  if (route.path === nav.path) return
  nav.handler()
}

/* ================= 加载用户信息 ================= */
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
      id: 5,
      username: 'A2023001',
      realName: '管理员',
      phone: '13800000005',
      role: 3,
      status: 1
    }
  }
}

/* ================= 加载待审核数量 ================= */
const loadPendingCount = async () => {
  try {
    // 通过管理员列表接口获取待审核数量
    const res = await axios.get('/api/item/admin/list', {
      params: {
        status: '1', // 待审核
        page: 1,
        size: 1
      }
    })
    if (res.data.code === 200) {
      pendingCount.value = res.data.data.statistics?.['待审核'] || 0
      stats.value.pending = pendingCount.value
    }
    
    // 更新时间
    const now = new Date()
    updateTime.value = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`
  } catch (error) {
    console.error('加载待审核数量失败:', error)
    pendingCount.value = 5 // 模拟数据
    stats.value.pending = 5
    
    // 更新时间
    const now = new Date()
    updateTime.value = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`
  }
}

/* ================= 退出登录处理 ================= */
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

/* ================= 生命周期 ================= */
onMounted(() => {
  loadUser()
  if (props.showStatsCard) {
    loadPendingCount()
  }
})

onUnmounted(() => {
  // 清理工作，防止内存泄漏
  console.log('AdminNavigation unmounted, key:', navKey.value)
})
</script>

<style scoped>
/* 左侧导航栏样式 - 添加will-change优化渲染 */
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
  z-index: 10;
  box-sizing: border-box;
  /* 防止重影：使用硬件加速和独立渲染层 */
  will-change: transform;
  transform: translateZ(0);
  backface-visibility: hidden;
  /* 防止动画残留 */
  animation: none !important;
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
  flex: 1;
  min-width: 0;
}

.user-nickname {
  font-family: "Comic Sans MS", "Marker Felt", cursive;
  font-size: 18px;
  font-weight: 600;
  color: #a67c52;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 管理员角色标签 */
.user-role-badge {
  font-family: "Comic Sans MS", cursive;
  font-size: 12px;
  color: white;
  background: linear-gradient(to right, #f38181, #f77d5f);
  padding: 2px 8px;
  border-radius: 10px;
  display: inline-block;
  margin-bottom: 4px;
  width: fit-content;
}

.user-subtitle {
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
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
  /* 防止按钮重影 */
  will-change: auto;
  transform: translateZ(0);
}

.left-nav-btn:hover {
  background: rgba(255, 255, 255, 0.15);
  transform: translateX(5px) translateZ(0);
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
  font-size: 18px;
}

/* 待审核数量红点 */
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

/* 左侧中间：快捷统计卡片 */
.left-notice-card {
  background: rgba(255, 255, 255, 0.15);
  border-radius: 14.4px;
  padding: 16px;
  margin: 15px 0;
  border: 1.6px solid rgba(166, 124, 82, 0.2);
  display: flex;
  flex-direction: column;
  width: 85%;
  max-height: 280px;
  min-height: 120px;
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: rgba(166, 124, 82, 0.15) transparent;
  box-sizing: border-box;
  /* 防止重影 */
  transform: translateZ(0);
}

.stats-content {
  flex: 1;
}

.stats-title {
  font-family: "Comic Sans MS", cursive;
  font-size: 16px;
  color: #a67c52;
  margin-bottom: 12px;
  font-weight: 600;
  text-align: center;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
}

.stat-label {
  color: rgba(166, 124, 82, 0.8);
}

.stat-value {
  font-weight: 600;
  color: #a67c52;
}

.stat-value.pending {
  color: #ff9800;
}

.stat-value.approved {
  color: #4caf50;
}

.stat-value.warning {
  color: #f44336;
}

.stats-time {
  font-family: "Comic Sans MS", cursive;
  font-size: 11px;
  color: rgba(166, 124, 82, 0.6);
  text-align: right;
  margin-top: 8px;
  flex-shrink: 0;
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
  /* 防止重影 */
  transform: translateZ(0);
}

.left-action-btn:hover {
  transform: translateX(5px) translateZ(0);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
}

.logout-btn {
  background: linear-gradient(to right, #f38181, #f77d5f);
  width: 75%;
  margin: 0 auto;
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
    /* 移动端重置transform */
    transform: none;
    will-change: auto;
  }

  /* 移动端隐藏用户信息、统计卡片 */
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
    transform: none;
  }

  .left-nav-btn:hover {
    transform: translateY(-2px);
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
    transform: none;
  }

  .left-action-btn:hover {
    transform: translateY(-2px);
  }

  .logout-btn {
    width: auto;
  }
}

/* 平板端适配（769px-1024px） */
@media (min-width: 769px) and (max-width: 1024px) {
  .left-nav {
    width: 260px;
  }
  
  .user-nickname {
    max-width: 120px;
  }
}
</style>