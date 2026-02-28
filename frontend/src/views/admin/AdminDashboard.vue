<template>
  <div class="admin-dashboard">
    <!-- 背景层 -->
    <div class="background-container">
      <div class="solid-background"></div>
    </div>

    <!-- 整体布局：左侧导航 + 右侧主内容 -->
    <div class="layout-container">
      <!-- 左侧导航栏 -->
      <aside class="admin-sidebar">
        <div class="sidebar-header">
          <h2 class="sidebar-title">失物招领管理</h2>
          <div class="user-info">
            <div class="user-avatar">
              <span class="avatar-text">{{ userInitials }}</span>
            </div>
            <div class="user-details">
              <div class="user-name">{{ userInfo.realName }}</div>
              <div class="user-role">管理员</div>
            </div>
          </div>
        </div>

        <nav class="sidebar-nav">
          <ul class="nav-list">
            <li 
              v-for="item in navItems" 
              :key="item.key"
              class="nav-item"
              :class="{ active: activeNav === item.key }"
              @click="switchNav(item.key)"
            >
              <span class="nav-icon">{{ item.icon }}</span>
              <span class="nav-text">{{ item.label }}</span>
            </li>
          </ul>
        </nav>

        <div class="sidebar-footer">
          <button class="logout-btn" @click="handleLogout">
            <span class="logout-icon">🚪</span>
            <span class="logout-text">退出登录</span>
          </button>
        </div>
      </aside>

      <!-- 右侧主内容区域 -->
      <main class="admin-main">
        <!-- 系统通知与公告页面 -->
        <div v-if="activeNav === 'notices'" class="notices-page">
          <div class="page-header">
            <h1 class="page-title">系统通知与公告</h1>
            <p class="page-subtitle">请仔细阅读以下重要通知</p>
          </div>

          <div class="notices-container">
            <!-- 重要通知 -->
            <div class="notice-card important">
              <div class="notice-header">
                <span class="notice-badge">重要</span>
                <h3 class="notice-title">📢 毕业季失物招领专场</h3>
                <span class="notice-time">2026-02-28</span>
              </div>
              <div class="notice-content">
                <p>毕业季期间，请各位管理员加强对失物招领信息的管理，及时处理积压物品，确保毕业生能够顺利找回失物。</p>
                <ul class="notice-list">
                  <li>• 加强对毕业季相关物品的审核</li>
                  <li>• 及时更新物品状态信息</li>
                  <li>• 做好物品交接记录</li>
                </ul>
              </div>
            </div>

            <!-- 常规通知 -->
            <div class="notice-card">
              <div class="notice-header">
                <span class="notice-badge">常规</span>
                <h3 class="notice-title">🔔 系统维护通知</h3>
                <span class="notice-time">2026-02-25</span>
              </div>
              <div class="notice-content">
                <p>系统将于每周日凌晨2:00-4:00进行例行维护，期间可能无法正常访问，请合理安排工作。</p>
              </div>
            </div>

            <!-- 操作指南 -->
            <div class="notice-card guide">
              <div class="notice-header">
                <span class="notice-badge">指南</span>
                <h3 class="notice-title">📋 管理员操作指南</h3>
                <span class="notice-time">2026-02-20</span>
              </div>
              <div class="notice-content">
                <p>请按照以下流程规范操作：</p>
                <ol class="guide-list">
                  <li>1. 每日登录系统查看待审核信息</li>
                  <li>2. 严格按照审核标准进行审核</li>
                  <li>3. 及时更新物品状态</li>
                  <li>4. 做好数据统计和记录</li>
                </ol>
              </div>
            </div>
          </div>

          <div class="action-section">
            <button class="confirm-btn" @click="enterMainInterface">
              确认并进入主界面
            </button>
          </div>
        </div>

        <!-- 审核发布信息页面 -->
        <div v-else-if="activeNav === 'audit'" class="audit-page">
          <AuditItemsView />
        </div>

        <!-- 管理物品状态页面 -->
        <div v-else-if="activeNav === 'manage'" class="manage-page">
          <ManageItemsView />
        </div>

        <!-- 信息维护与查询页面 -->
        <div v-else-if="activeNav === 'query'" class="query-page">
          <QueryStatisticsView />
        </div>

        <!-- 默认显示通知页面 -->
        <div v-else class="notices-page">
          <!-- 内容同上 -->
        </div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, defineAsyncComponent } from 'vue'
import { useRouter } from 'vue-router'
// 动态导入组件，避免循环依赖
const AuditItemsView = defineAsyncComponent(() => import('./AuditItemsView.vue'))
const ManageItemsView = defineAsyncComponent(() => import('./ManageItemsView.vue'))
const QueryStatisticsView = defineAsyncComponent(() => import('./QueryStatisticsView.vue'))

const router = useRouter()

// 用户信息
const userInfo = ref({
  realName: sessionStorage.getItem('realName') || '管理员',
  username: sessionStorage.getItem('username') || ''
})

// 导航项
const navItems = ref([
  { key: 'notices', label: '系统通知', icon: '📢' },
  { key: 'audit', label: '审核信息', icon: '✅' },
  { key: 'manage', label: '状态管理', icon: '📊' },
  { key: 'query', label: '信息查询', icon: '🔍' }
])

const activeNav = ref('notices')

// 计算用户姓名首字母
const userInitials = computed(() => {
  const name = userInfo.value.realName
  return name ? name.charAt(0) : '管'
})

// 切换导航
const switchNav = (navKey: string) => {
  activeNav.value = navKey
}

// 进入主界面
const enterMainInterface = () => {
  activeNav.value = 'audit'
}

// 退出登录
const handleLogout = () => {
  // 清除用户信息
  sessionStorage.clear()
  // 跳转到登录页
  router.push('/admin/login')
}

onMounted(() => {
  // 检查是否已登录
  const userId = sessionStorage.getItem('userId')
  const role = sessionStorage.getItem('role')
  
  if (!userId || role !== '3') {
    // 如果不是管理员或未登录，跳转到登录页
    router.push('/admin/login')
  }
})
</script>

<style scoped>
.admin-dashboard {
  min-height: 100vh;
  background: #f5f5f5;
}

.background-container {
  position: fixed;
  inset: 0;
  z-index: 0;
}

.solid-background {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.layout-container {
  display: flex;
  min-height: 100vh;
  position: relative;
  z-index: 1;
}

/* 左侧导航栏样式 */
.admin-sidebar {
  width: 280px;
  background: #fff;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  z-index: 2;
}

.sidebar-header {
  padding: 24px 20px;
  border-bottom: 1px solid #f0f0f0;
}

.sidebar-title {
  font-size: 18px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 20px 0;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 16px;
}

.user-details {
  flex: 1;
}

.user-name {
  font-size: 14px;
  font-weight: 500;
  color: #1a1a1a;
  margin-bottom: 2px;
}

.user-role {
  font-size: 12px;
  color: #666;
}

.sidebar-nav {
  flex: 1;
  padding: 20px 0;
}

.nav-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  border-left: 3px solid transparent;
}

.nav-item:hover {
  background: #f8f9fa;
}

.nav-item.active {
  background: #e3f2fd;
  border-left-color: #007bff;
  color: #007bff;
}

.nav-icon {
  font-size: 18px;
  margin-right: 12px;
  width: 24px;
  text-align: center;
}

.nav-text {
  font-size: 14px;
  font-weight: 500;
}

.sidebar-footer {
  padding: 20px;
  border-top: 1px solid #f0f0f0;
}

.logout-btn {
  width: 100%;
  padding: 10px;
  background: #f8f9fa;
  border: 1px solid #ddd;
  border-radius: 6px;
  color: #666;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.logout-btn:hover {
  background: #e9ecef;
  color: #333;
}

/* 右侧主内容区域 */
.admin-main {
  flex: 1;
  background: #f8f9fa;
  overflow-y: auto;
}

/* 通知页面样式 */
.notices-page {
  padding: 32px;
  max-width: 800px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 40px;
}

.page-title {
  font-size: 28px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 8px 0;
}

.page-subtitle {
  font-size: 16px;
  color: #666;
  margin: 0;
}

.notices-container {
  margin-bottom: 40px;
}

.notice-card {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border-left: 4px solid #007bff;
}

.notice-card.important {
  border-left-color: #e53e3e;
}

.notice-card.guide {
  border-left-color: #38a169;
}

.notice-header {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
  gap: 12px;
}

.notice-badge {
  background: #007bff;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.notice-card.important .notice-badge {
  background: #e53e3e;
}

.notice-card.guide .notice-badge {
  background: #38a169;
}

.notice-title {
  font-size: 18px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0;
  flex: 1;
}

.notice-time {
  font-size: 12px;
  color: #999;
}

.notice-content {
  color: #666;
  line-height: 1.6;
}

.notice-list {
  margin: 12px 0 0 0;
  padding-left: 20px;
}

.guide-list {
  margin: 12px 0 0 0;
  padding-left: 20px;
}

.notice-list li,
.guide-list li {
  margin-bottom: 4px;
}

.action-section {
  text-align: center;
}

.confirm-btn {
  background: #007bff;
  color: white;
  border: none;
  padding: 12px 32px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.confirm-btn:hover {
  background: #0056b3;
  transform: translateY(-1px);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .layout-container {
    flex-direction: column;
  }
  
  .admin-sidebar {
    width: 100%;
    height: auto;
  }
  
  .notices-page {
    padding: 20px 16px;
  }
  
  .page-title {
    font-size: 24px;
  }
}
</style>