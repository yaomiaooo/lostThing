<template>
  <div class="home-page">
    <!-- 纯色背景 -->
    <div class="background-container">
      <div class="solid-background"></div>
    </div>

    <!-- 整体布局：左侧导航 + 右侧主内容 -->
    <div class="layout-container">
      <!-- 左侧导航栏组件 -->
    <Navigation 
      subtitle="欢迎回来^_^"
      active-nav="消息"
      :unread-count="totalUnreadCount"
      :custom-content="true"
      @logout="handleLogout"
    >
      <template #custom-content>
        <div class="notice-content">
          <div class="notice-title">💬 消息统计</div>
          <div class="notice-desc">总会话：{{ stats.total }} | 未读：{{ stats.unread }} | 活跃：{{ stats.active }}</div>
        </div>
        <div class="notice-time">今日更新</div>
      </template>
    </Navigation>

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
          <button class="error-action-btn" @click="() => loadConversations()">重试</button>
        </div>

        <!-- 会话列表 -->
        <div v-else class="conversations-container">
          <!-- 下拉刷新提示 -->
          <div v-if="refreshing" class="refresh-indicator">
            <div class="refresh-spinner"></div>
            <span>正在刷新...</span>
          </div>

          <div 
            v-for="conversation in sortedConversations" 
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
              <div 
                v-if="conversation.unreadCount > 0" 
                class="unread-badge"
              >
                {{ conversation.unreadCount > 99 
                  ? '99+' 
                  : Math.max(1, conversation.unreadCount) 
                }}
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
                <span 
                  class="last-message" 
                  :class="{ 
                    'unread-text': conversation.unreadCount > 0 
                  }"
                >
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
      @message-sent="handleMessageSent"
    />
  </div>
</template>

<script setup lang="ts">
import {
  ref,
  onMounted,
  reactive,
  computed,
  watch,
  onUnmounted,
  onActivated,
  onDeactivated,
  nextTick
} from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import DetailMessagesView from './DetailMessagesView.vue'
import Navigation from './navigation.vue'
import {
  useRealtimeMessages,
  UnreadCountManager,
  type RealtimeCallback
} from '../../utils/realtimeService'

// 路由实例
const router = useRouter()
const route = useRoute()

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
const isMessagesPageActive = ref(false)

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

// ==================== 实时消息服务 ====================
const { subscribe, unsubscribe, unsubscribeAll, triggerUpdate, addProcessedMessageId, setUserId } = useRealtimeMessages()

// ==================== 未读计数计算属性 ====================
const totalUnreadCount = computed(() => {
  // 直接计算所有会话的未读计数之和，确保与各会话红点同步
  return conversations.value.reduce((sum, conv) => {
    const unreadCount = typeof conv.unreadCount === 'number' ? Math.max(0, conv.unreadCount) : 0
    return sum + unreadCount
  }, 0)
})

// 获取单个对话的未读计数
const getConversationUnreadCount = (conversationId: number): number => {
  if (!conversationId) return 0
  
  // 直接从会话数据中获取未读计数，确保与数据同步
  const conversation = conversations.value.find(c => c.conversationId === conversationId)
  if (!conversation) return 0
  
  const unreadCount = typeof conversation.unreadCount === 'number' 
    ? Math.max(0, conversation.unreadCount) 
    : 0
  
  return unreadCount
}

// 按未读状态和时间排序的会话列表
const sortedConversations = computed(() => {
  return [...conversations.value].sort((a, b) => {
    const unreadA = typeof a.unreadCount === 'number' ? Math.max(0, a.unreadCount) : 0
    const unreadB = typeof b.unreadCount === 'number' ? Math.max(0, b.unreadCount) : 0

    if (unreadA > 0 && unreadB === 0) return -1
    if (unreadA === 0 && unreadB > 0) return 1

    const timeA = new Date(a.lastTime || 0).getTime()
    const timeB = new Date(b.lastTime || 0).getTime()
    return timeB - timeA
  })
})

// ==================== 统计信息 ====================
const stats = computed(() => {
  const total = conversations.value.length
  const unread = totalUnreadCount.value
  const active = conversations.value.filter(conv => conv.lastTime).length

  return { total, unread, active }
})

// ==================== 导航函数 ====================
const goHome = () => router.push('/home')
const goPublish = () => router.push('/publish')
const goMessages = () => {
  if (route.path === '/messages') {
    refreshList()
  } else {
    router.push('/messages')
  }
}
const goMyPosts = () => router.push('/my-posts')
const goSettings = () => router.push('/settings')



// ==================== 全局实时消息处理器（关键修复）====================
const handleRealtimeUpdate: RealtimeCallback = (update) => {
  if (!update.messages || update.messages.length === 0) return

  const latestMsg = update.messages[update.messages.length - 1]
  const targetId = update.conversationId
  const index = conversations.value.findIndex(c => c.conversationId === targetId)

  if (index !== -1) {
    const conv = conversations.value[index]
    conv.lastMessage = latestMsg.content
    conv.lastTime = latestMsg.createTime || latestMsg.createdAt
    
    // --- 修复未读数逻辑：避免重复计数 ---
    // 只有当"聊天弹窗未打开"或者"打开的不是当前这个会话"时，才增加未读数
    if (!chatDialogVisible.value || activeConversationId.value !== targetId) {
      // 确保 unreadCount 存在且为数字
      if (typeof conv.unreadCount !== 'number' || isNaN(conv.unreadCount)) {
        conv.unreadCount = 0
      }
      
      // 只增加新消息的数量，避免重复计数
      // 假设 update.messages 只包含新收到的消息
      const newMessagesCount = update.messages.filter(msg => {
        // 检查消息时间是否比当前最后消息时间新
        const msgTime = new Date(msg.createTime || msg.createdAt)
        const lastTime = new Date(conv.lastTime)
        return msgTime > lastTime
      }).length
      
      // 如果没有找到更新的消息，默认增加1条
      const actualNewCount = newMessagesCount > 0 ? newMessagesCount : 1
      conv.unreadCount += actualNewCount
      
      // 强制更新计算属性，确保消息按钮红点同步更新
      conversations.value = [...conversations.value]
    }

    // 移至顶部
    conversations.value.splice(index, 1)
    conversations.value.unshift(conv)
  } else {
    loadConversations()
  }
}

// ==================== 数据加载（关键修复）====================
async function loadUser() {
  try {
    const res = await axios.get('/api/user/info')
    if (res.data.code === 0) {
      user.value = res.data.data

      // 同步到 sessionStorage
      sessionStorage.setItem('userId', user.value.id.toString())
      sessionStorage.setItem('userInfo', JSON.stringify(user.value))

      // 关键修复：设置 userId 到 realtimeService
      setUserId(user.value.id)

      // 同步服务端未读数（覆盖本地旧数据）
      await UnreadCountManager.syncWithServer(user.value.id)

      // 初始化订阅
      setTimeout(() => {
        initializeConversationsSubscription()
      }, 100)
    }
  } catch (error) {
    console.error('加载用户信息失败:', error)
    const cachedUser = sessionStorage.getItem('userInfo')
    const cachedUserId = sessionStorage.getItem('userId')
    if (cachedUser && cachedUserId) {
      try {
        user.value = JSON.parse(cachedUser)
        setUserId(parseInt(cachedUserId))
        await UnreadCountManager.syncWithServer(parseInt(cachedUserId))
      } catch (e) {
        console.error('恢复用户信息失败')
      }
    }
  }
}

// 初始化所有对话的订阅
const initializeConversationsSubscription = async () => {
  if (!user.value.id) return

  try {
    const response = await axios.get('/api/chat/conversation/list')
    if (response.data.code === 0) {
      const data = response.data.data || []

      data.forEach((conv: any) => {
        if (conv.conversationId) {
          subscribe(conv.conversationId, handleRealtimeUpdate)
        }
      })

      console.log(`[MessagesView] 初始化了 ${data.length} 个对话的订阅`)
    }
  } catch (err) {
    console.error('[MessagesView] 初始化对话订阅失败:', err)
  }
}

const loadConversations = async (showLoading = true) => {
  if (loading.value) return

  if (showLoading) {
    loading.value = true
  }
  error.value = ''

  try {
    const response = await axios.get('/api/chat/conversation/list')
    if (response.data.code === 0) {
      const data = response.data.data || []
      const currentUserId = user.value.id

      // 关键修复：以服务端未读数为准，重置本地数据
      UnreadCountManager.clearAll(currentUserId)

      const processedConversations = data.map((conv: any) => {
        const conversationId = conv.conversationId

        if (conversationId) {
          subscribe(conversationId, handleRealtimeUpdate)
        }

        // 使用服务端未读数
        const unreadCount = typeof conv.unreadCount === 'number' ? conv.unreadCount : 0
        if (unreadCount > 0) {
          UnreadCountManager.setUnreadCount(currentUserId, conversationId, unreadCount)
        }

        return {
          ...conv,
          unreadCount
        }
      })

      conversations.value = processedConversations
      hasMore.value = data.length === pageSize

      console.log(`[MessagesView] 加载了 ${data.length} 个会话，总未读: ${totalUnreadCount.value}`)
    } else {
      error.value = response.data.msg || '加载失败'
    }
  } catch (err) {
    error.value = '网络不稳定，请点击重试'
    console.error('[MessagesView] 加载会话列表失败:', err)
  } finally {
    loading.value = false
    refreshing.value = false
  }
}

const loadMore = async () => {
  if (loadingMore.value || !hasMore.value) return

  loadingMore.value = true

  try {
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

  // 关键修复：刷新时重新同步服务端数据
  if (user.value.id) {
    await UnreadCountManager.syncWithServer(user.value.id)
  }

  conversations.value.forEach(conv => {
    if (conv.conversationId) {
      triggerUpdate(conv.conversationId)
    }
  })

  await loadConversations()
}

// ==================== 会话操作（关键修复）====================
const openConversation = async (conversation: any) => {
  const conversationId = conversation.conversationId
  const currentUserId = user.value.id

  if (!conversationId || !currentUserId) return

  activeConversationId.value = conversationId
  // --- 核心修改：清除未读数 ---
  conversation.unreadCount = 0 
  
  // 强制更新视图，确保红点立即消失
  conversations.value = [...conversations.value]

  // 记录打开时间戳
  const now = Date.now()
  const lastReadKey = `last_read_time_${currentUserId}_${conversationId}`
  localStorage.setItem(lastReadKey, now.toString())

  // 清除未读计数
  UnreadCountManager.clearUnreadCount(currentUserId, conversationId)

  // 关键修复：将当前对话的现有消息标记为已处理
  await markConversationMessagesAsProcessed(conversationId)

  // 打开对话框
  currentConversationId.value = conversationId
  currentItemId.value = conversation.itemId || 0
  dialogTitle.value = conversation.itemName || '聊天'
  chatDialogVisible.value = true
}

// 标记对话消息为已处理
const markConversationMessagesAsProcessed = async (conversationId: number) => {
  try {
    const response = await axios.get('/api/chat/conversation/messages', {
      params: { conversationId, limit: 50 }
    })

    if (response.data.code === 0 && response.data.data.messages) {
      const messages = response.data.data.messages
      messages.forEach((msg: any) => {
        const messageId = msg.id || msg.messageId || `${msg.senderId}_${msg.createTime}_${msg.content?.slice(0, 30)}_${msg.sequence || 0}`
        addProcessedMessageId(conversationId, messageId)
      })
      console.log(`[MessagesView] 已标记 ${messages.length} 条消息为已处理`)
    }
  } catch (err) {
    console.error('标记消息已处理失败:', err)
  }
}

const closeChatDialog = () => {
  chatDialogVisible.value = false
  currentConversationId.value = undefined
  currentItemId.value = 0
  dialogTitle.value = ''
  activeConversationId.value = null

  setTimeout(() => {
    if (isMessagesPageActive.value) {
      loadConversations(false)
    }
  }, 300)
}

const handleMessageSent = (data: { conversationId: number }) => {
  setTimeout(() => {
    triggerUpdate(data.conversationId)
  }, 500)
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

// 退出登录处理
const handleLogout = async () => {
  const userId = user.value.id

  try {
    if (userId) {
      await axios.post('/api/user/logout', { userId })
    }
  } catch (error) {
    console.error('退出登录失败:', error)
  } finally {
    // 清理未读计数
    if (userId) {
      UnreadCountManager.clearAll(userId)
    }

    // 清理登录态
    sessionStorage.clear()

    // 重置实时服务
    unsubscribeAll()

    router.replace('/login')
  }
}

// ==================== 生命周期 ====================
onMounted(async () => {
  console.log('[MessagesView] 组件挂载')

  // 关键修复：先设置 userId 到 realtimeService
  const cachedUserId = sessionStorage.getItem('userId')
  if (cachedUserId) {
    setUserId(parseInt(cachedUserId))
  }

  await loadUser()

  isMessagesPageActive.value = true
  await loadConversations()

  window.addEventListener('unread-count-changed', handleUnreadCountChanged as EventListener)
  window.addEventListener('storage', handleStorageChange as EventListener)
})

const handleUnreadCountChanged = (event: CustomEvent) => {
  const { userId: eventUserId, conversationId, count } = event.detail
  if (eventUserId === user.value.id) {
    conversations.value = [...conversations.value]
    console.log(`[MessagesView] 未读计数变化: 对话 ${conversationId} = ${count}`)
  }
}

const handleStorageChange = (e: StorageEvent) => {
  if (e.key?.startsWith('unread_count_')) {
    conversations.value = [...conversations.value]
  }
}

onActivated(async () => {
  console.log('[MessagesView] 组件激活')
  isMessagesPageActive.value = true

  // 关键修复：激活时重新同步服务端数据
  if (user.value.id) {
    await UnreadCountManager.syncWithServer(user.value.id)
  }

  await nextTick()
  await loadConversations(false)
})

onDeactivated(() => {
  console.log('[MessagesView] 组件失活')
  isMessagesPageActive.value = false
})

onUnmounted(() => {
  console.log('[MessagesView] 组件卸载')
  isMessagesPageActive.value = false
  window.removeEventListener('unread-count-changed', handleUnreadCountChanged as EventListener)
  window.removeEventListener('storage', handleStorageChange as EventListener)
})
</script>

<style scoped>
/* 样式部分保持不变，添加导航栏红点样式 */
.nav-badge {
  position: absolute;
  top: 8px;
  right: 8px;
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
  animation: pulse-badge 2s infinite;
}

@keyframes pulse-badge {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.left-nav-btn {
  position: relative;
}

/* 其他样式保持不变... */
.home-page {
  width: 100vw;
  min-height: 100vh;
  position: relative;
  overflow: hidden;
}

.background-container {
  position: fixed;  
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
  overflow: hidden;
}

.solid-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: #f8f3d4;
  pointer-events: none;
}

.layout-container {
  position: relative;
  z-index: 2;
  width: 100%;
  min-height: 100vh;
  display: flex;
}

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

.nav-top-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 8px;
}

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

.nav-bottom-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: auto;
}

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

.main-content {
  flex: 1;
  min-height: 100vh;
  padding: 24px 28px;
  margin-left: 288px;
  max-width: calc(100vw - 288px);
  box-sizing: border-box;
}

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

@media (max-width: 768px) {
  .layout-container {
    flex-direction: column;
  }

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

  .user-info-container,
  .left-notice-card {
    display: none;
  }

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
  
  .nav-badge {
    top: 2px;
    right: 2px;
    padding: 1px 4px;
    font-size: 9px;
    min-width: 14px;
  }

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

  .main-content {
    margin-left: 0;
    max-width: 100vw;
    padding: 25px 20px;
    padding-bottom: 90px;
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