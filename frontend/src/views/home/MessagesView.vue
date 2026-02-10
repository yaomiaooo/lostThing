<template>
  <div class="home-page">
    <!-- 纯色背景 -->
    <div class="background-container">
      <!-- 背景层 -->
      <div class="solid-background"></div>
    </div>

    <!-- 整体布局：左侧导航 + 右侧主内容 -->
    <div class="layout-container">
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
            <div class="user-subtitle">欢迎回来^_^</div>
          </div>
        </div>

        <!-- 左侧上半区：核心导航 -->
        <div class="nav-top-group">
          <button 
              v-for="nav in navItems" 
              :key="nav.name"
              class="left-nav-btn"
              :class="{ active: nav.active }"
              @click="nav.handler"
            >
              <span class="nav-icon">
                <img :src="nav.icon" :alt="nav.name" class="nav-svg" />
              </span>
              <span class="nav-text">{{ nav.name }}</span>
            </button>
        </div>

        <!-- 左侧中间：公告栏 -->
        <div class="left-notice-card bubble">
          <div class="notice-content">
            <div class="notice-title">💬 消息统计</div>
            <div class="notice-desc">总会话：{{ stats.total }} | 未读：{{ stats.unread }} | 活跃：{{ stats.active }}</div>
          </div>
          <div class="notice-time">今日更新</div>
        </div>

        <!-- 左侧下半区：操作按钮 -->
        <div class="nav-bottom-group">
          <button 
            class="left-action-btn logout-btn"
            @click="logout"
          >
            <span class="btn-text">退出登录</span>
          </button>
        </div>
      </aside>

      <!-- 右侧主内容区域 -->
      <main class="main-content">
        <!-- 页面标题和操作区 -->
        <section class="page-header">
          <div class="header-left">
            <h1 class="page-title">我的消息</h1>
            <div class="subtitle">查看和管理您的所有沟通会话</div>
          </div>
          <div class="header-right">
            <button class="refresh-btn" @click="refreshList" :disabled="loading">
              <span class="btn-text">{{ loading ? '刷新中...' : '刷新' }}</span>
            </button>
          </div>
        </section>

        <!-- 加载状态 -->
        <div v-if="loading && conversations.length === 0" class="loading-container">
          <div class="loading-spinner"></div>
          <div class="loading-text">正在加载会话列表...</div>
        </div>

        <!-- 空数据状态 -->
        <div v-else-if="!loading && conversations.length === 0" class="empty-container">
          <div class="empty-icon">💬</div>
          <div class="empty-title">暂无消息会话</div>
          <div class="empty-desc">还没有任何沟通会话，去首页看看物品吧</div>
          <button class="empty-action-btn" @click="goHome">前往首页</button>
        </div>

        <!-- 错误状态 -->
        <div v-else-if="error" class="error-container">
          <div class="error-icon">⚠️</div>
          <div class="error-title">加载失败</div>
          <div class="error-desc">{{ error }}</div>
          <button class="error-action-btn" @click="loadConversations">重试</button>
        </div>

        <!-- 会话列表 -->
        <div v-else class="conversations-container">
          <!-- 下拉刷新提示 -->
          <div v-if="refreshing" class="refresh-indicator">
            <div class="refresh-spinner"></div>
            <span>正在刷新...</span>
          </div>

          <div 
            v-for="conversation in conversations" 
            :key="conversation.conversationId"
            class="conversation-item"
            :class="{ 
              'unread': conversation.unreadCount > 0,
              'active': activeConversationId === conversation.conversationId 
            }"
            @click="openConversation(conversation)"
          >
            <div class="conversation-avatar">
              <div class="avatar-placeholder">
                {{ conversation.itemName ? conversation.itemName.charAt(0) : '物' }}
              </div>
              <div v-if="conversation.unreadCount > 0" class="unread-badge">
                {{ conversation.unreadCount > 99 ? '99+' : conversation.unreadCount }}
              </div>
            </div>

            <div class="conversation-content">
              <div class="conversation-header">
                <div class="conversation-title">
                  <span class="item-name">{{ conversation.itemName }}</span>
                  <span class="role-tag" :class="conversation.myRole">
                    {{ conversation.myRole === 'owner' ? '失主' : '拾主' }}
                  </span>
                </div>
                <div class="conversation-time">
                  {{ formatTime(conversation.lastTime) }}
                </div>
              </div>

              <div class="conversation-preview">
                <span class="last-message" :class="{ 'unread-text': conversation.unreadCount > 0 }">
                  {{ conversation.lastMessage || '暂无消息' }}
                </span>
              </div>
            </div>

            <div class="conversation-arrow">›</div>
          </div>

          <!-- 加载更多 -->
          <div v-if="hasMore" class="load-more-container">
            <button 
              class="load-more-btn" 
              @click="loadMore" 
              :disabled="loadingMore"
            >
              {{ loadingMore ? '加载中...' : '加载更多' }}
            </button>
          </div>

          <!-- 没有更多数据提示 -->
          <div v-else-if="conversations.length > 0" class="no-more-container">
            <div class="no-more-text">没有更多会话了</div>
          </div>
        </div>
      </main>
    </div>

    <!-- 聊天对话框 -->
    <DetailMessagesView
      :visible="chatDialogVisible"
      :conversation-id="currentConversationId"
      :item-id="currentItemId"
      :dialog-title="dialogTitle"
      @update:visible="chatDialogVisible = $event"
      @close="closeChatDialog"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import DetailMessagesView from './DetailMessagesView.vue'
// 导入实时消息服务
import { useRealtimeMessages, type RealtimeCallback } from '../../utils/realtimeService'
// 路由实例
const router = useRouter()

// ==================== 状态管理 ====================
const conversations = ref<any[]>([])
const loading = ref(false)
const loadingMore = ref(false)
const refreshing = ref(false)
const error = ref('')
const hasMore = ref(true)
const currentPage = ref(1)
const pageSize = 20
const activeConversationId = ref<number | null>(null)


// ==================== 聊天对话框状态 ====================
const chatDialogVisible = ref(false)
const currentConversationId = ref<number | undefined>(undefined)
const currentItemId = ref<number>(0)
const dialogTitle = ref('')

// ==================== 用户信息 ====================
const user = ref({
  id: 0,
  username: '',
  realName: '加载中...',
  phone: '',
  role: 0,
  status: 0
})

// ==================== 统计信息 ====================
const stats = computed(() => {
  const total = conversations.value.length
  const unread = conversations.value.reduce((sum, conv) => sum + (conv.unreadCount || 0), 0)
  const active = conversations.value.filter(conv => conv.lastTime).length
  
  return { total, unread, active }
})

// ==================== 导航函数 ====================
const goHome = () => router.push('/home')
const goPublish = () => router.push('/publish')
const goMessages = () => {}
const goMyPosts = () => router.push('/my-posts')
const goSettings = () => router.push('/settings')

// ==================== 左侧导航栏 ====================
const navItems = reactive([
  {
    name: '发现',
    icon: '/home/发现.svg',
    active: false,
    handler: goHome
  },
  {
    name: '发布',
    icon: '/home/发布.svg',
    active: false,
    handler: goPublish
  },
  {
    name: '消息',
    icon: '/home/消息.svg',
    active: true,
    handler: goMessages
  },
  {
    name: '我的',
    icon: '/home/我的.svg',
    active: false,
    handler: goMyPosts
  },
  {
    name: '设置',
    icon: '/home/设置.svg',
    active: false,
    handler: goSettings
  }
])

// ==================== 生命周期 ====================
onMounted(() => {
  loadUser()
  loadConversations()
})

// ==================== 数据加载 ====================
async function loadUser() {
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
      username: '2023123456',
      realName: '齐司礼',
      phone: '13800000001',
      role: 1,
      status: 1
    }
  }
}

// 实时消息 Hook
const { subscribe, unsubscribe } = useRealtimeMessages()

// ==================== 核心逻辑：处理实时更新 ====================
const handleGlobalRealtimeUpdate: RealtimeCallback = (update) => {
  if (!update.messages || update.messages.length === 0) return

  const latestMsg = update.messages[update.messages.length - 1]
  const targetId = update.conversationId
  const index = conversations.value.findIndex(c => c.conversationId === targetId)

  if (index !== -1) {
    const conv = conversations.value[index]
    conv.lastMessage = latestMsg.content
    conv.lastTime = latestMsg.createTime || latestMsg.createdAt
    
    // --- 核心修改：未读数逻辑 ---
    // 只有当“聊天弹窗未打开”或者“打开的不是当前这个会话”时，才增加未读数
    if (!chatDialogVisible.value || activeConversationId.value !== targetId) {
      // 如果后端没返回 unreadCount 字段，前端初始化它
      if (conv.unreadCount === undefined) conv.unreadCount = 0
      conv.unreadCount += update.messages.length
    }

    // 移至顶部
    conversations.value.splice(index, 1)
    conversations.value.unshift(conv)
  } else {
    loadConversations()
  }
}

const loadConversations = async () => {
  if (loading.value) return
  loading.value = true
  error.value = ''
  
  try {
    const response = await axios.get('/api/chat/conversation/list')
    if (response.data.code === 0) {
      const data = response.data.data || []
      conversations.value = data
      
      // 加载完成后，确保所有会话都已订阅
      data.forEach((conv: any) => {
        subscribe(conv.conversationId, handleGlobalRealtimeUpdate)
      })
      
      hasMore.value = data.length === pageSize
    } else {
      error.value = response.data.msg || '加载失败'
    }
  } catch (err) {
    // 错误处理机制
    error.value = '网络不稳定，请点击重试'
    console.error('加载会话列表失败:', err)
  } finally {
    loading.value = false
    refreshing.value = false
  }
}

const loadMore = async () => {
  if (loadingMore.value || !hasMore.value) return
  
  loadingMore.value = true
  
  try {
    // 实际项目中需要分页接口
    // const response = await axios.get('/api/chat/conversation/list', {
    //   params: { page: currentPage.value + 1, size: pageSize }
    // })
    
    // 模拟加载更多
    setTimeout(() => {
      hasMore.value = false
      loadingMore.value = false
    }, 1000)
  } catch (err) {
    console.error('加载更多失败:', err)
    loadingMore.value = false
  }
}

const refreshList = async () => {
  if (refreshing.value) return
  
  refreshing.value = true
  currentPage.value = 1
  await loadConversations()
}

// ==================== 会话操作 ====================
// 修改打开会话的函数，点击后清空红点
const openConversation = (conversation: any) => {
  activeConversationId.value = conversation.conversationId
  // --- 核心修改：清除未读数 ---
  conversation.unreadCount = 0 
  
  currentConversationId.value = conversation.conversationId
  currentItemId.value = conversation.itemId || 0
  dialogTitle.value = `${conversation.itemName}`
  chatDialogVisible.value = true
}

const closeChatDialog = () => {
  chatDialogVisible.value = false
  currentConversationId.value = undefined
  currentItemId.value = 0
  dialogTitle.value = ''
}

// ==================== 工具函数 ====================
const formatTime = (timeStr: string) => {
  if (!timeStr) return ''
  
  try {
    const date = new Date(timeStr)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    
    if (diff < 60 * 1000) return '刚刚'
    if (diff < 60 * 60 * 1000) return `${Math.floor(diff / (60 * 1000))}分钟前`
    if (diff < 24 * 60 * 60 * 1000) return `${Math.floor(diff / (60 * 60 * 1000))}小时前`
    if (diff < 7 * 24 * 60 * 60 * 1000) return `${Math.floor(diff / (24 * 60 * 60 * 1000))}天前`
    
    return date.toLocaleDateString('zh-CN')
  } catch {
    return timeStr
  }
}

async function logout() {
  try {
    const userId = user.value.id
    if (userId) {
      await axios.post('/api/user/logout', { userId })
    }
  } catch (error) {
    console.error('退出登录失败:', error)
  } finally {
    // 清理所有存储
    localStorage.clear()
    sessionStorage.clear()
    
    // 使用 replace 而不是 push，避免路由守卫拦截
    router.replace('/login')
  }
}
</script>

<style scoped>
/* 继承 HomeView.vue 的基础样式 */
.home-page {
  width: 100vw;
  min-height: 100vh;
  position: relative;
  overflow: hidden;
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

/* 左侧导航栏 */
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
}

/* 左侧用户信息区域 */
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
}

.left-nav-btn.active {
  background: rgba(243, 129, 129, 0.15);
  font-weight: 600;
}

.left-nav-btn:hover {
  background: rgba(255, 255, 255, 0.15);
  transform: translateX(5px);
}

.left-nav-btn .nav-icon {
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

.left-nav-btn .nav-text {
  font-size: 20px;
}

/* 左侧中间：公告栏 */
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

/* 右侧主内容区 */
.main-content {
  flex: 1;
  min-height: 100vh;
  padding: 24px 28px;
  margin-left: 288px;
  max-width: calc(100vw - 288px);
  box-sizing: border-box;
}

/* 页面标题和操作区 */
.page-header {
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(15px);
  border-radius: 20px;
  padding: 25px;
  border: 2px solid rgba(166, 124, 82, 0.2);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
  margin-bottom: 25px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  flex: 1;
}

.page-title {
  font-family: "Comic Sans MS", "Marker Felt", cursive;
  font-size: 28px;
  color: #a67c52;
  font-weight: 700;
  margin-bottom: 8px;
}

.subtitle {
  font-family: "Comic Sans MS", cursive;
  font-size: 16px;
  color: rgba(166, 124, 82, 0.8);
}

/* 刷新按钮 */
.refresh-btn {
  padding: 12.8px 22.4px;
  border-radius: 19.2px;
  border: none;
  background: linear-gradient(135deg, #f38181, #f77d5f);
  color: white;
  font-family: "Comic Sans MS", cursive;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(243, 129, 129, 0.3);
}

.refresh-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(243, 129, 129, 0.4);
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: 0 4px 12px rgba(243, 129, 129, 0.2);
}

/* 状态容器样式 */
.loading-container,
.empty-container,
.error-container {
  background: rgba(255, 255, 255, 0.35);
  backdrop-filter: blur(15px);
  border-radius: 20px;
  padding: 60px 20px;
  border: 2px solid rgba(166, 124, 82, 0.2);
  text-align: center;
  margin-bottom: 25px;
}

.loading-spinner,
.refresh-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(166, 124, 82, 0.1);
  border-top: 3px solid #f38181;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  font-family: "Comic Sans MS", cursive;
  font-size: 16px;
  color: #a67c52;
}

.empty-icon,
.error-icon {
  font-size: 48px;
  margin-bottom: 16px;
  color: #a67c52;
}

.empty-title,
.error-title {
  font-family: "Comic Sans MS", "Marker Felt", cursive;
  font-size: 20px;
  color: #a67c52;
  font-weight: 600;
  margin-bottom: 8px;
}

.empty-desc,
.error-desc {
  font-family: "Comic Sans MS", cursive;
  font-size: 16px;
  color: rgba(166, 124, 82, 0.8);
  margin-bottom: 20px;
  max-width: 300px;
  margin-left: auto;
  margin-right: auto;
  line-height: 1.5;
}

.empty-action-btn,
.error-action-btn,
.load-more-btn {
  padding: 12.8px 22.4px;
  border-radius: 19.2px;
  border: none;
  background: linear-gradient(135deg, #f38181, #f77d5f);
  color: white;
  font-family: "Comic Sans MS", cursive;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(243, 129, 129, 0.3);
}

.empty-action-btn:hover,
.error-action-btn:hover,
.load-more-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(243, 129, 129, 0.4);
}

.load-more-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: 0 4px 12px rgba(243, 129, 129, 0.2);
}

/* 会话列表容器 */
.conversations-container {
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(15px);
  border-radius: 20px;
  padding: 25px;
  border: 2px solid rgba(166, 124, 82, 0.2);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
  max-height: calc(100vh - 250px);
  overflow-y: auto;
}

.refresh-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 10px;
  color: #a67c52;
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  margin-bottom: 15px;
}

.refresh-spinner {
  width: 16px;
  height: 16px;
  margin: 0 8px 0 0;
}

/* 会话项样式 */
.conversation-item {
  background: rgba(255, 255, 255, 0.35);
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1.6px solid rgba(166, 124, 82, 0.2);
}

.conversation-item:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
  border-color: rgba(243, 129, 129, 0.5);
}

.conversation-item.active {
  background: rgba(243, 129, 129, 0.15);
  border-color: rgba(243, 129, 129, 0.7);
}

.conversation-item.unread {
  background: rgba(255, 107, 107, 0.1);
  border-color: rgba(255, 107, 107, 0.3);
}

.conversation-avatar {
  position: relative;
  margin-right: 16px;
}

.avatar-placeholder {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: linear-gradient(135deg, #f38181, #f77d5f);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-family: "Comic Sans MS", cursive;
  font-size: 20px;
  font-weight: 600;
  box-shadow: 0 4px 10px rgba(243, 129, 129, 0.3);
}

.unread-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  background: #ff6b6b;
  color: white;
  border-radius: 10px;
  padding: 2px 6px;
  font-family: "Comic Sans MS", cursive;
  font-size: 10px;
  font-weight: 600;
  min-width: 18px;
  text-align: center;
  box-shadow: 0 2px 6px rgba(255, 107, 107, 0.3);
}

.conversation-content {
  flex: 1;
  min-width: 0;
}

.conversation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.conversation-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.item-name {
  font-family: "Comic Sans MS", "Marker Felt", cursive;
  font-size: 18px;
  font-weight: 600;
  color: #a67c52;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 200px;
}

.role-tag {
  font-family: "Comic Sans MS", cursive;
  font-size: 11.2px;
  padding: 4px 8px;
  border-radius: 9.6px;
  font-weight: 600;
}

.role-tag.owner {
  background: linear-gradient(135deg, #ff9a9e 0%, #fad0c4 100%);
  color: #a67c52;
}

.role-tag.finder {
  background: linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%);
  color: #a67c52;
}

.conversation-time {
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: rgba(166, 124, 82, 0.7);
  white-space: nowrap;
  margin-left: 10px;
}

.conversation-preview {
  font-family: "Comic Sans MS", cursive;
  font-size: 16px;
  color: rgba(166, 124, 82, 0.8);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.last-message.unread-text {
  color: #a67c52;
  font-weight: 600;
}

.conversation-arrow {
  font-family: "Comic Sans MS", cursive;
  color: rgba(166, 124, 82, 0.6);
  font-size: 24px;
  margin-left: 12px;
  transition: all 0.3s ease;
}

.conversation-item:hover .conversation-arrow {
  color: #f38181;
  transform: translateX(3px);
}

/* 加载更多容器 */
.load-more-container,
.no-more-container {
  display: flex;
  justify-content: center;
  padding: 20px;
}

.no-more-text {
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: rgba(166, 124, 82, 0.6);
}

/* 响应式设计：移动端（768px以下） */
@media (max-width: 768px) {
  .layout-container {
    flex-direction: column;
  }

  /* 左侧导航移至底部，横向布局 */
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

  /* 右侧主内容区 */
  .main-content {
    margin-left: 0;
    max-width: 100vw;
    padding: 25px 20px;
    padding-bottom: 90px; /* 给底部导航留空间 */
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }

  .header-right {
    align-self: stretch;
  }

  .refresh-btn {
    width: 100%;
  }

  .conversations-container {
    max-height: calc(100vh - 350px);
  }

  .conversation-item {
    padding: 15px;
  }

  .avatar-placeholder {
    width: 40px;
    height: 40px;
    font-size: 16px;
  }

  .item-name {
    max-width: 150px;
  }
}

/* 平板端适配（769px-1024px） */
@media (min-width: 769px) and (max-width: 1024px) {
  .left-nav {
    width: 300px;
  }

  .main-content {
    margin-left: 300px;
    max-width: calc(100vw - 300px);
  }
  
  .user-nickname {
    max-width: 120px;
  }
  
  .conversations-container {
    max-height: calc(100vh - 280px);
  }
}
</style>