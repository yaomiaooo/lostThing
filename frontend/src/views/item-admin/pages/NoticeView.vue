<!-- src/views/item-admin/pages/NoticeView.vue -->
<template>
  <div class="notice-page">
    <!-- 纯色背景 -->
    <div class="background-container">
      <div class="solid-background"></div>
    </div>

    <!-- 整体布局 -->
    <div class="layout-container">
      <!-- 左侧导航栏 -->
      <AdminNavigation 
        subtitle="请确认公告"
        active-nav="通知公告"
        :show-stats-card="false"
        @logout="handleLogout"
      />

      <!-- 右侧主内容区域 -->
      <main class="main-content">
        <!-- 页面标题 -->
        <section class="page-header">
          <h1 class="page-title">📢 系统通知与公告</h1>
          <p class="page-subtitle">请仔细阅读以下公告，确认后进入工作台</p>
        </section>

        <!-- 公告列表 -->
        <section class="notice-list-section">
          <!-- 加载状态 -->
          <div v-if="loading" class="loading-container">
            <div class="loading-spinner"></div>
            <div class="loading-text">加载公告中...</div>
          </div>

          <!-- 空状态 -->
          <div v-else-if="notices.length === 0 && notifications.length === 0" class="empty-container">
            <div class="empty-icon">📭</div>
            <div class="empty-title">暂无新公告</div>
            <div class="empty-desc">您已阅读所有系统通知</div>
            <button class="confirm-btn" @click="enterDashboard">
              进入工作台
            </button>
          </div>

          <!-- 公告内容 -->
          <div v-else class="notice-content">
            <!-- 未读通知提示 -->
            <div v-if="totalUnread > 0" class="unread-banner">
              <span class="unread-icon">🔔</span>
              <span class="unread-text">您有 {{ totalUnread }} 条未读通知</span>
            </div>

            <!-- 系统公告列表 -->
            <div v-if="notices.length > 0" class="notice-group">
              <h2 class="group-title">📋 系统公告</h2>
              <div 
                v-for="notice in notices" 
                :key="'notice-'+notice.id"
                class="notice-card"
                :class="{ unread: !notice.read }"
              >
                <div class="notice-header">
                  <span class="notice-type" :class="'type-'+notice.type">
                    {{ getNoticeTypeText(notice.type) }}
                  </span>
                  <span class="notice-time">{{ formatTime(notice.createTime) }}</span>
                </div>
                <h3 class="notice-title-text">{{ notice.title }}</h3>
                <div class="notice-body">
                  <p class="notice-content-text">{{ notice.content }}</p>
                </div>
                <div class="notice-footer">
                  <span class="notice-publisher">发布人：{{ notice.publisher }}</span>
                  <button 
                    v-if="!notice.read" 
                    class="mark-read-btn"
                    @click="markNoticeRead(notice.id)"
                  >
                    标记已读
                  </button>
                </div>
              </div>
            </div>

            <!-- 个人通知列表 -->
            <div v-if="notifications.length > 0" class="notice-group">
              <h2 class="group-title">✉️ 个人通知</h2>
              <div 
                v-for="notification in notifications" 
                :key="'notif-'+notification.id"
                class="notice-card notification-card"
                :class="{ unread: !notification.read }"
              >
                <div class="notice-header">
                  <span class="notice-type" :class="'type-'+notification.type">
                    {{ getNotificationTypeText(notification.type) }}
                  </span>
                  <span class="notice-time">{{ formatTime(notification.createTime) }}</span>
                </div>
                <h3 class="notice-title-text">{{ notification.title }}</h3>
                <div class="notice-body">
                  <p class="notice-content-text">{{ notification.content }}</p>
                </div>
                <div class="notice-footer">
                  <span class="related-info" v-if="notification.relatedItem">
                    关联物品：{{ notification.relatedItem }}
                  </span>
                  <button 
                    v-if="!notification.read" 
                    class="mark-read-btn"
                    @click="markNotificationRead(notification.id)"
                  >
                    标记已读
                  </button>
                </div>
              </div>
            </div>

            <!-- 底部确认按钮 -->
            <div class="confirm-section">
              <label class="confirm-checkbox">
                <input 
                  type="checkbox" 
                  v-model="hasReadAll"
                  :disabled="totalUnread > 0"
                />
                <span class="custom-checkbox"></span>
                <span class="confirm-text" :class="{ disabled: totalUnread > 0 }">
                  我已阅读并知晓上述公告内容
                </span>
              </label>
              <button 
                class="enter-btn"
                :class="{ disabled: !hasReadAll || totalUnread > 0 }"
                :disabled="!hasReadAll || totalUnread > 0"
                @click="enterDashboard"
              >
                进入工作台
              </button>
            </div>
          </div>
        </section>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import AdminNavigation from '../components/AdminNavigation.vue'

const router = useRouter()

/* ================= 数据状态 ================= */
const loading = ref(true)
const notices = ref<any[]>([])
const notifications = ref<any[]>([])
const hasReadAll = ref(false)

/* ================= 计算属性 ================= */
const totalUnread = computed(() => {
  const unreadNotices = notices.value.filter(n => !n.read).length
  const unreadNotifications = notifications.value.filter(n => !n.read).length
  return unreadNotices + unreadNotifications
})

/* ================= 加载公告数据 ================= */
const loadNotices = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/announcements')
    if (res.data.code === 200) {
      notices.value = res.data.data.announcements || []
      notifications.value = res.data.data.unreadNotifications || []
      
      // 检查是否需要强制确认
      if (!res.data.data.needConfirm && totalUnread.value === 0) {
        // 没有需要确认的内容，自动进入
        hasReadAll.value = true
      }
    }
  } catch (error) {
    console.error('加载公告失败:', error)
    // 模拟数据
    notices.value = [
      {
        id: 1,
        type: 'system',
        title: '系统维护通知',
        content: '系统将于本周六凌晨2:00-4:00进行例行维护，期间可能无法访问，请提前安排工作。',
        publisher: '系统管理员',
        createTime: '2026-02-28 10:00:00',
        read: false
      },
      {
        id: 2,
        type: 'policy',
        title: '审核规范更新',
        content: '请严格按照新的审核标准执行：1.照片必须清晰可辨 2.信息描述必须完整 3.联系方式必须有效。不符合要求的请直接驳回。',
        publisher: '失物招领中心',
        createTime: '2026-02-27 14:30:00',
        read: false
      }
    ]
    notifications.value = [
      {
        id: 1,
        type: 'claim',
        title: '新的认领申请',
        content: '有新的认领申请需要您审核，请及时处理。',
        relatedItem: '待审核申请',
        createTime: '2026-02-28 09:15:00',
        read: false
      }
    ]
  } finally {
    loading.value = false
  }
}

/* ================= 标记已读 ================= */
const markNoticeRead = async (noticeId: number) => {
  try {
    const res = await axios.post('/api/announcements/read', {
      noticeIds: [noticeId],
      notificationIds: []
    })
    if (res.data.code === 200) {
      const notice = notices.value.find(n => n.id === noticeId)
      if (notice) notice.read = true
    }
  } catch (error) {
    console.error('标记已读失败:', error)
    // 前端模拟
    const notice = notices.value.find(n => n.id === noticeId)
    if (notice) notice.read = true
  }
}

const markNotificationRead = async (notificationId: number) => {
  try {
    const res = await axios.post('/api/announcements/read', {
      noticeIds: [],
      notificationIds: [notificationId]
    })
    if (res.data.code === 200) {
      const notification = notifications.value.find(n => n.id === notificationId)
      if (notification) notification.read = true
    }
  } catch (error) {
    console.error('标记已读失败:', error)
    // 前端模拟
    const notification = notifications.value.find(n => n.id === notificationId)
    if (notification) notification.read = true
  }
}

/* ================= 进入工作台 ================= */
const enterDashboard = () => {
  if (!hasReadAll.value || totalUnread.value > 0) return
  
  // 标记所有为已读
  markAllAsRead()
  
  // 跳转到待审核页面（管理员主界面）
  router.push('/item-admin/pending')
}

const markAllAsRead = async () => {
  try {
    const unreadNoticeIds = notices.value.filter(n => !n.read).map(n => n.id)
    const unreadNotificationIds = notifications.value.filter(n => !n.read).map(n => n.id)
    
    if (unreadNoticeIds.length > 0 || unreadNotificationIds.length > 0) {
      await axios.post('/api/announcements/read', {
        noticeIds: unreadNoticeIds,
        notificationIds: unreadNotificationIds
      })
    }
  } catch (error) {
    console.error('批量标记已读失败:', error)
  }
}

/* ================= 工具函数 ================= */
const getNoticeTypeText = (type: string) => {
  const typeMap: Record<string, string> = {
    'system': '系统',
    'policy': '政策',
    'notice': '公告',
    'urgent': '紧急'
  }
  return typeMap[type] || '公告'
}

const getNotificationTypeText = (type: number) => {
  const typeMap: Record<number, string> = {
    1: '审核',
    2: '认领',
    3: '系统',
    4: '提醒'
  }
  return typeMap[type] || '通知'
}

const formatTime = (timeStr: string) => {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  
  // 今天
  if (date.toDateString() === now.toDateString()) {
    return `今天 ${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`
  }
  
  // 昨天
  const yesterday = new Date(now)
  yesterday.setDate(yesterday.getDate() - 1)
  if (date.toDateString() === yesterday.toDateString()) {
    return `昨天 ${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`
  }
  
  // 一周内
  if (diff < 7 * 24 * 60 * 60 * 1000) {
    const days = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
    return days[date.getDay()]
  }
  
  // 更早
  return `${date.getMonth() + 1}月${date.getDate()}日`
}

/* ================= 退出登录 ================= */
const handleLogout = () => {
  router.push('/login')
}

/* ================= 生命周期 ================= */
onMounted(() => {
  loadNotices()
})
</script>

<style scoped>
/* 基础布局 */
.notice-page {
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

/* 整体布局 */
.layout-container {
  position: relative;
  z-index: 2;
  width: 100%;
  min-height: 100vh;
  display: flex;
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

/* 页面标题 */
.page-header {
  margin-bottom: 25px;
  text-align: center;
}

.page-title {
  font-family: "Comic Sans MS", "Marker Felt", cursive;
  font-size: 32px;
  color: #a67c52;
  margin: 0 0 10px 0;
  font-weight: 700;
}

.page-subtitle {
  font-family: "Comic Sans MS", cursive;
  font-size: 16px;
  color: rgba(166, 124, 82, 0.7);
}

/* 公告列表区域 */
.notice-list-section {
  min-height: 400px;
}

/* 加载状态 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 0;
  background: rgba(255, 255, 255, 0.35);
  backdrop-filter: blur(15px);
  border-radius: 20px;
  border: 2px solid rgba(166, 124, 82, 0.2);
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(166, 124, 82, 0.2);
  border-top-color: #a67c52;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  font-family: "Comic Sans MS", cursive;
  font-size: 18px;
  color: rgba(166, 124, 82, 0.8);
}

/* 空状态 */
.empty-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 0;
  background: rgba(255, 255, 255, 0.35);
  backdrop-filter: blur(15px);
  border-radius: 20px;
  border: 2px solid rgba(166, 124, 82, 0.2);
  text-align: center;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 20px;
  opacity: 0.6;
}

.empty-title {
  font-family: "Comic Sans MS", "Marker Felt", cursive;
  font-size: 24px;
  color: #a67c52;
  margin-bottom: 12px;
  font-weight: 600;
}

.empty-desc {
  font-family: "Comic Sans MS", cursive;
  font-size: 16px;
  color: rgba(166, 124, 82, 0.7);
  margin-bottom: 25px;
}

/* 公告内容区域 */
.notice-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 未读提示横幅 */
.unread-banner {
  background: linear-gradient(135deg, #f38181, #f77d5f);
  color: white;
  padding: 15px 25px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  font-family: "Comic Sans MS", cursive;
  font-size: 16px;
  box-shadow: 0 4px 15px rgba(243, 129, 129, 0.3);
  animation: pulse-banner 2s infinite;
}

@keyframes pulse-banner {
  0%, 100% { box-shadow: 0 4px 15px rgba(243, 129, 129, 0.3); }
  50% { box-shadow: 0 6px 25px rgba(243, 129, 129, 0.5); }
}

.unread-icon {
  font-size: 20px;
}

/* 公告分组 */
.notice-group {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.group-title {
  font-family: "Comic Sans MS", cursive;
  font-size: 20px;
  color: #a67c52;
  margin: 0 0 5px 0;
  font-weight: 600;
  padding-left: 10px;
  border-left: 4px solid #f38181;
}

/* 公告卡片 */
.notice-card {
  background: rgba(255, 255, 255, 0.35);
  backdrop-filter: blur(15px);
  border-radius: 16px;
  padding: 20px;
  border: 2px solid rgba(166, 124, 82, 0.2);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.notice-card.unread {
  border-color: rgba(243, 129, 129, 0.5);
  background: rgba(255, 255, 255, 0.45);
  box-shadow: 0 4px 20px rgba(243, 129, 129, 0.1);
}

.notice-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
}

/* 个人通知卡片特殊样式 */
.notification-card {
  border-left: 4px solid #4caf50;
}

.notification-card.unread {
  border-left-color: #ff9800;
}

/* 公告头部 */
.notice-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.notice-type {
  padding: 4px 12px;
  border-radius: 12px;
  font-family: "Comic Sans MS", cursive;
  font-size: 12px;
  font-weight: 600;
  color: white;
}

/* 公告类型颜色 */
.type-system { background: #2196f3; }
.type-policy { background: #9c27b0; }
.type-notice { background: #607d8b; }
.type-urgent { background: #f44336; }
.type-1 { background: #ff9800; } /* 审核 */
.type-2 { background: #4caf50; } /* 认领 */
.type-3 { background: #2196f3; } /* 系统 */
.type-4 { background: #9c27b0; } /* 提醒 */

.notice-time {
  font-family: "Comic Sans MS", cursive;
  font-size: 13px;
  color: rgba(166, 124, 82, 0.6);
}

/* 公告标题 */
.notice-title-text {
  font-family: "Comic Sans MS", "Marker Felt", cursive;
  font-size: 18px;
  color: #a67c52;
  margin: 0 0 10px 0;
  font-weight: 600;
  line-height: 1.4;
}

/* 公告内容 */
.notice-body {
  margin-bottom: 15px;
}

.notice-content-text {
  font-family: "Comic Sans MS", cursive;
  font-size: 15px;
  color: rgba(166, 124, 82, 0.9);
  line-height: 1.6;
  margin: 0;
}

/* 公告底部 */
.notice-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 15px;
  border-top: 1px solid rgba(166, 124, 82, 0.1);
}

.notice-publisher {
  font-family: "Comic Sans MS", cursive;
  font-size: 13px;
  color: rgba(166, 124, 82, 0.6);
}

.related-info {
  font-family: "Comic Sans MS", cursive;
  font-size: 13px;
  color: #4caf50;
  background: rgba(76, 175, 80, 0.1);
  padding: 4px 10px;
  border-radius: 8px;
}

/* 标记已读按钮 */
.mark-read-btn {
  padding: 6px 14px;
  border: none;
  border-radius: 8px;
  background: linear-gradient(to right, #f38181, #f77d5f);
  color: white;
  font-family: "Comic Sans MS", cursive;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.mark-read-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(243, 129, 129, 0.3);
}

/* 确认区域 */
.confirm-section {
  background: rgba(255, 255, 255, 0.35);
  backdrop-filter: blur(15px);
  border-radius: 16px;
  padding: 25px;
  border: 2px solid rgba(166, 124, 82, 0.2);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  margin-top: 10px;
}

/* 确认复选框 */
.confirm-checkbox {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
}

.confirm-checkbox input {
  display: none;
}

.custom-checkbox {
  width: 22px;
  height: 22px;
  border: 2px solid rgba(166, 124, 82, 0.4);
  border-radius: 6px;
  position: relative;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.3);
  flex-shrink: 0;
}

.confirm-checkbox input:checked + .custom-checkbox {
  background: linear-gradient(to right, #f38181, #f77d5f);
  border-color: #f38181;
}

.confirm-checkbox input:checked + .custom-checkbox::after {
  content: '✓';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: white;
  font-size: 14px;
  font-weight: bold;
}

.confirm-text {
  font-family: "Comic Sans MS", cursive;
  font-size: 16px;
  color: #a67c52;
  font-weight: 500;
}

.confirm-text.disabled {
  color: rgba(166, 124, 82, 0.5);
}

/* 进入按钮 */
.enter-btn {
  padding: 14px 40px;
  border: none;
  border-radius: 12px;
  background: linear-gradient(to right, #f38181, #f77d5f);
  color: white;
  font-family: "Comic Sans MS", cursive;
  font-size: 18px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(243, 129, 129, 0.3);
}

.enter-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(243, 129, 129, 0.4);
}

.enter-btn:disabled,
.enter-btn.disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* 空状态进入按钮 */
.confirm-btn {
  padding: 12px 30px;
  border: none;
  border-radius: 12px;
  background: linear-gradient(to right, #f38181, #f77d5f);
  color: white;
  font-family: "Comic Sans MS", cursive;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(243, 129, 129, 0.3);
}

.confirm-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(243, 129, 129, 0.4);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .main-content {
    margin-left: 0;
    max-width: 100vw;
    padding: 20px 15px;
    padding-bottom: 100px;
  }

  .page-title {
    font-size: 24px;
  }

  .page-subtitle {
    font-size: 14px;
  }

  .notice-card {
    padding: 15px;
  }

  .notice-title-text {
    font-size: 16px;
  }

  .notice-content-text {
    font-size: 14px;
  }

  .confirm-section {
    padding: 20px 15px;
  }

  .enter-btn {
    width: 100%;
    padding: 12px 20px;
    font-size: 16px;
  }
}

@media (min-width: 769px) and (max-width: 1024px) {
  .main-content {
    margin-left: 260px;
    max-width: calc(100vw - 260px);
    padding: 20px;
  }
}
</style>