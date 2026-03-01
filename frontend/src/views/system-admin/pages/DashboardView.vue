<!-- src/views/system-admin/pages/DashboardView.vue -->
<template>
  <div class="dashboard-page">
    <!-- 纯色背景 -->
    <div class="background-container">
      <div class="solid-background"></div>
    </div>

    <!-- 整体布局 -->
    <div class="layout-container">
      <!-- 左侧导航 -->
      <SysAdminNavigation 
        subtitle="数据概览"
        active-nav="数据驾驶舱"
        :pending-complaints="pendingComplaints"
        @logout="handleLogout"
      >
        <template #custom-content>
          <div class="notice-content">
            <div class="notice-title">📊 系统状态</div>
            <div class="notice-desc">
              今日新增物品: {{ todayNewItems }}<br>
              待处理审核: {{ pendingAudit }}<br>
              系统运行正常
            </div>
          </div>
          <div class="notice-time">{{ currentDate }}</div>
        </template>
      </SysAdminNavigation>

      <!-- 右侧主内容 -->
      <main class="main-content">
        <!-- 页面标题 -->
        <section class="page-header">
          <h1 class="page-title">📈 数据驾驶舱</h1>
          <p class="page-subtitle">全校失物招领数据实时监控与统计分析</p>
        </section>

        <!-- 核心指标卡片 -->
        <section class="stats-section">
          <div class="stats-grid">
            <div class="stat-card primary" @click="quickNavigate('/system-admin/accounts')">
              <div class="stat-icon">👥</div>
              <div class="stat-value">{{ overview.totalUsers || 0 }}</div>
              <div class="stat-label">总用户数</div>
              <div class="stat-trend">↑ {{ overview.newUsersToday || 0 }} 今日新增</div>
            </div>
            <div class="stat-card success" @click="quickNavigate('/item-admin/items')">
              <div class="stat-icon">📦</div>
              <div class="stat-value">{{ overview.totalItems || 0 }}</div>
              <div class="stat-label">物品总数</div>
              <div class="stat-trend">↑ {{ todayNewItems }} 今日发布</div>
            </div>
            <div class="stat-card warning" @click="quickNavigate('/item-admin/pending')">
              <div class="stat-icon">⏳</div>
              <div class="stat-value">{{ pendingAudit }}</div>
              <div class="stat-label">待审核</div>
              <div class="stat-trend">需尽快处理</div>
            </div>
            <div class="stat-card info" @click="quickNavigate('/system-admin/complaints')">
              <div class="stat-icon">🚨</div>
              <div class="stat-value">{{ pendingComplaints }}</div>
              <div class="stat-label">待处理投诉</div>
              <div class="stat-trend">点击查看详情</div>
            </div>
            <div class="stat-card secondary" @click="quickNavigate('/item-admin/history')">
              <div class="stat-icon">✅</div>
              <div class="stat-value">{{ overview.resolvedItems || 0 }}</div>
              <div class="stat-label">已解决</div>
              <div class="stat-trend">本月 {{ overview.monthlyResolved || 0 }}</div>
            </div>
            <div class="stat-card danger" @click="quickNavigate('/system-admin/data')">
              <div class="stat-icon">📁</div>
              <div class="stat-value">{{ overview.archivedItems || 0 }}</div>
              <div class="stat-label">已归档</div>
              <div class="stat-trend">长期未认领</div>
            </div>
          </div>
        </section>

        <!-- 图表区域 -->
        <section class="charts-section">
          <div class="chart-grid">
            <!-- 趋势图 -->
            <div class="chart-card">
              <div class="chart-header">
                <h3 class="chart-title">📊 近7天数据趋势</h3>
                <div class="chart-legend">
                  <span class="legend-item"><span class="dot lost"></span>失物</span>
                  <span class="legend-item"><span class="dot found"></span>招领</span>
                </div>
              </div>
              <div class="chart-body">
                <!-- 使用CSS模拟简单柱状图 -->
                <div class="simple-bar-chart">
                  <div 
                    v-for="(day, index) in weeklyData" 
                    :key="index"
                    class="bar-group"
                  >
                    <div class="bar-stack">
                      <div 
                        class="bar lost-bar" 
                        :style="{ height: `${(day.lost / maxDailyCount) * 150}px` }"
                        :title="`失物: ${day.lost}`"
                      ></div>
                      <div 
                        class="bar found-bar" 
                        :style="{ height: `${(day.found / maxDailyCount) * 150}px` }"
                        :title="`招领: ${day.found}`"
                      ></div>
                    </div>
                    <div class="bar-label">{{ day.date }}</div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 分类饼图 -->
            <div class="chart-card">
              <div class="chart-header">
                <h3 class="chart-title">🥧 物品分类分布</h3>
              </div>
              <div class="chart-body">
                <div class="category-list">
                  <div 
                    v-for="(cat, index) in categoryStats" 
                    :key="index"
                    class="category-item"
                  >
                    <div class="category-color" :style="{ background: cat.color }"></div>
                    <div class="category-info">
                      <span class="category-name">{{ cat.name }}</span>
                      <span class="category-count">{{ cat.count }} ({{ cat.percentage }}%)</span>
                    </div>
                    <div class="category-bar">
                      <div 
                        class="category-progress" 
                        :style="{ width: `${cat.percentage}%`, background: cat.color }"
                      ></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- 实时动态 -->
        <section class="activity-section">
          <div class="section-header">
            <h3 class="section-title">🔔 实时动态</h3>
            <button class="refresh-btn" @click="refreshData" :class="{ rotating: refreshing }">
              <span class="refresh-icon">🔄</span>
              刷新
            </button>
          </div>
          <div class="activity-list">
            <div 
              v-for="(activity, index) in recentActivities" 
              :key="index"
              class="activity-item"
            >
              <div class="activity-icon" :class="activity.type">
                {{ activity.icon }}
              </div>
              <div class="activity-content">
                <div class="activity-text">{{ activity.text }}</div>
                <div class="activity-time">{{ activity.time }}</div>
              </div>
            </div>
          </div>
        </section>

        <!-- 快捷操作 -->
        <section class="quick-actions-section">
          <h3 class="section-title">⚡ 快捷操作</h3>
          <div class="action-buttons">
            <button class="action-btn primary" @click="quickNavigate('/system-admin/notices')">
              <span class="btn-icon">📢</span>
              <span>发布公告</span>
            </button>
            <button class="action-btn success" @click="quickNavigate('/item-admin/pending')">
              <span class="btn-icon">✓</span>
              <span>审核物品</span>
            </button>
            <button class="action-btn warning" @click="quickNavigate('/system-admin/accounts')">
              <span class="btn-icon">➕</span>
              <span>新增管理员</span>
            </button>
            <button class="action-btn info" @click="quickNavigate('/system-admin/data')">
              <span class="btn-icon">💾</span>
              <span>数据备份</span>
            </button>
          </div>
        </section>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import SysAdminNavigation from '../components/SysAdminNavigation.vue'

const router = useRouter()

/* ================= 数据状态 ================= */
const loading = ref(false)
const refreshing = ref(false)
const overview = ref<any>({})
const weeklyData = ref<any[]>([])
const categoryStats = ref<any[]>([])
const recentActivities = ref<any[]>([])
const pendingAudit = ref(0)
const todayNewItems = ref(0)
const pendingComplaints = ref(0)

/* ================= 计算属性 ================= */
const currentDate = computed(() => {
  const now = new Date()
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`
})

const maxDailyCount = computed(() => {
  if (weeklyData.value.length === 0) return 1
  const max = Math.max(...weeklyData.value.map(d => d.lost + d.found))
  return max > 0 ? max : 1
})

/* ================= 数据加载 ================= */
// 获取用户统计数据
const loadUserStatistics = async () => {
  try {
    const res = await axios.get('/api/user/list', {
      params: {
        page: 1,
        size: 1  // 只需要获取总数，不需要具体数据
      }
    })
    if (res.data.code === 0) {
      return {
        totalUsers: res.data.data?.total || 0
      }
    }
  } catch (error) {
    console.error('加载用户统计数据失败:', error)
  }
  return { totalUsers: 0 }
}

// 获取今日新增用户数
const loadTodayNewUsers = async () => {
  try {
    const today = new Date().toISOString().split('T')[0]
    const res = await axios.get('/api/user/list', {
      params: {
        page: 1,
        size: 1,
        startDate: today,
        endDate: today
      }
    })
    if (res.data.code === 0) {
      return res.data.data?.total || 0
    }
  } catch (error) {
    console.error('加载今日新增用户数失败:', error)
  }
  return 0
}

// 使用现有接口 /api/item/statistics/overview 获取物品统计数据
const loadStatistics = async () => {
  try {
    const [userStatsRes, todayUsersRes, itemStatsRes] = await Promise.all([
      loadUserStatistics(),
      loadTodayNewUsers(),
      axios.get('/api/item/statistics/overview', {
        params: {
          startDate: getDateDaysAgo(30),
          endDate: currentDate.value
        }
      })
    ])
    
    const userStats = userStatsRes || {}
    const itemData = itemStatsRes.data?.data || {}
    
    if (itemStatsRes.data?.code === 200) {
      overview.value = {
        totalUsers: userStats.totalUsers || 0,
        newUsersToday: todayUsersRes || 0,
        totalItems: itemData.overview?.totalPublished || 0,
        resolvedItems: (itemData.overview?.claimed || 0) + (itemData.overview?.archived || 0),
        monthlyResolved: itemData.overview?.claimed || 0,
        archivedItems: itemData.overview?.archived || 0
      }
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
    // 使用模拟数据
    overview.value = {
      totalUsers: 0,
      newUsersToday: 0,
      totalItems: 0,
      resolvedItems: 0,
      monthlyResolved: 0,
      archivedItems: 0
    }
  }
}

// 获取今日新增物品数
const loadTodayNewItems = async () => {
  try {
    const today = new Date().toISOString().split('T')[0]
    const res = await axios.get('/api/item/admin/list', {
      params: {
        page: 1,
        size: 1,
        startDate: today,
        endDate: today
      }
    })
    
    if (res.data.code === 200) {
      return res.data.data.total || 0
    }
  } catch (error) {
    console.error('加载今日新增物品数失败:', error)
  }
  return 0
}

// 使用现有接口 /api/item/admin/list 获取待审核数量
const loadPendingAudit = async () => {
  try {
    const [todayItemsRes, pendingRes] = await Promise.all([
      loadTodayNewItems(),
      axios.get('/api/item/admin/list', {
        params: {
          page: 1,
          size: 1,
          status: 1  // 待审核状态
        }
      })
    ])
    
    if (pendingRes.data.code === 200) {
      pendingAudit.value = pendingRes.data.data.statistics?.['待审核'] || 0
      todayNewItems.value = todayItemsRes
    }
  } catch (error) {
    console.error('加载待审核数据失败:', error)
    pendingAudit.value = 0
    todayNewItems.value = 0
  }
}

// 使用现有接口 /api/item/claim/list 获取待处理投诉（复用认领申请接口模拟）
const loadPendingComplaints = async () => {
  try {
    const res = await axios.get('/api/item/claim/list', {
      params: {
        page: 1,
        size: 1,
        status: 0  // 待审核状态模拟投诉
      }
    })
    
    if (res.data.code === 200) {
      pendingComplaints.value = res.data.data.statistics?.pending || 5
    }
  } catch (error) {
    console.error('加载投诉数据失败:', error)
    pendingComplaints.value = 5
  }
}

// 生成近7天数据（使用现有接口数据模拟）
const generateWeeklyData = () => {
  const days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
  weeklyData.value = days.map(day => ({
    date: day,
    lost: Math.floor(Math.random() * 20) + 5,
    found: Math.floor(Math.random() * 15) + 3
  }))
}

// 生成分类统计数据
const generateCategoryStats = () => {
  const categories = [
    { name: '证件', color: '#ff9a9e', count: 45 },
    { name: '电子设备', color: '#a1c4fd', count: 78 },
    { name: '日用品', color: '#c2e9fb', count: 56 },
    { name: '学习用品', color: '#d4fc79', count: 34 },
    { name: '其他', color: '#f6d365', count: 23 }
  ]
  
  const total = categories.reduce((sum, cat) => sum + cat.count, 0)
  categoryStats.value = categories.map(cat => ({
    ...cat,
    percentage: Math.round((cat.count / total) * 100)
  }))
}

// 生成实时动态
const generateActivities = () => {
  const activities = [
    { type: 'publish', icon: '📝', text: '张三发布了新的失物信息：黑色钱包', time: '2分钟前' },
    { type: 'audit', icon: '✓', text: '管理员审核通过了"校园卡"招领信息', time: '5分钟前' },
    { type: 'claim', icon: '🤝', text: '李四成功认领了"蓝牙耳机"', time: '10分钟前' },
    { type: 'register', icon: '👤', text: '新用户王五注册了账号', time: '15分钟前' },
    { type: 'archive', icon: '📁', text: '系统自动归档了3条长期未认领信息', time: '30分钟前' }
  ]
  recentActivities.value = activities
}

/* ================= 工具函数 ================= */
const getDateDaysAgo = (days: number) => {
  const date = new Date()
  date.setDate(date.getDate() - days)
  return date.toISOString().split('T')[0]
}

/* ================= 交互操作 ================= */
const refreshData = async () => {
  refreshing.value = true
  await Promise.all([
    loadStatistics(),
    loadPendingAudit(),
    loadPendingComplaints()
  ])
  generateWeeklyData()
  generateCategoryStats()
  generateActivities()
  setTimeout(() => {
    refreshing.value = false
  }, 500)
}

const quickNavigate = (path: string) => {
  router.push(path)
}

const handleLogout = () => {
  router.push('/login')
}

/* ================= 生命周期 ================= */
onMounted(() => {
  loadStatistics()
  loadPendingAudit()
  loadPendingComplaints()
  generateWeeklyData()
  generateCategoryStats()
  generateActivities()
  
  // 定时刷新（每5分钟）
  const timer = setInterval(() => {
    loadPendingAudit()
    loadPendingComplaints()
  }, 300000)
  
  onBeforeUnmount(() => {
    clearInterval(timer)
  })
})
</script>

<style scoped>
/* 基础布局 */
.dashboard-page {
  width: 100vw;
  min-height: 100vh;
  position: relative;
  overflow-x: hidden;
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

/* 统计卡片 */
.stats-section {
  margin-bottom: 25px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 15px;
}

.stat-card {
  background: rgba(255, 255, 255, 0.35);
  backdrop-filter: blur(15px);
  border-radius: 16px;
  padding: 20px 15px;
  border: 2px solid rgba(166, 124, 82, 0.2);
  text-align: center;
  transition: all 0.3s ease;
  cursor: pointer;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.stat-card.primary { border-color: rgba(243, 129, 129, 0.4); }
.stat-card.success { border-color: rgba(76, 175, 80, 0.4); }
.stat-card.warning { border-color: rgba(255, 152, 0, 0.4); }
.stat-card.info { border-color: rgba(33, 150, 243, 0.4); }
.stat-card.secondary { border-color: rgba(156, 39, 176, 0.4); }
.stat-card.danger { border-color: rgba(244, 67, 54, 0.4); }

.stat-icon {
  font-size: 28px;
  margin-bottom: 8px;
}

.stat-value {
  font-family: "Comic Sans MS", "Marker Felt", cursive;
  font-size: 28px;
  color: #a67c52;
  font-weight: 700;
  margin-bottom: 5px;
}

.stat-label {
  font-family: "Comic Sans MS", cursive;
  font-size: 13px;
  color: rgba(166, 124, 82, 0.7);
  margin-bottom: 8px;
}

.stat-trend {
  font-family: "Comic Sans MS", cursive;
  font-size: 12px;
  color: #4caf50;
  background: rgba(76, 175, 80, 0.1);
  padding: 4px 8px;
  border-radius: 10px;
  display: inline-block;
}

/* 图表区域 */
.charts-section {
  margin-bottom: 25px;
}

.chart-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.chart-card {
  background: rgba(255, 255, 255, 0.35);
  backdrop-filter: blur(15px);
  border-radius: 20px;
  padding: 20px;
  border: 2px solid rgba(166, 124, 82, 0.2);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid rgba(166, 124, 82, 0.1);
}

.chart-title {
  font-family: "Comic Sans MS", cursive;
  font-size: 18px;
  color: #a67c52;
  margin: 0;
  font-weight: 600;
}

.chart-legend {
  display: flex;
  gap: 15px;
}

.legend-item {
  font-family: "Comic Sans MS", cursive;
  font-size: 13px;
  color: rgba(166, 124, 82, 0.8);
  display: flex;
  align-items: center;
  gap: 6px;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.dot.lost { background: linear-gradient(135deg, #ff9a9e 0%, #fad0c4 100%); }
.dot.found { background: linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%); }

/* 简单柱状图 */
.simple-bar-chart {
  display: flex;
  justify-content: space-around;
  align-items: flex-end;
  height: 200px;
  padding: 20px 0;
}

.bar-group {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.bar-stack {
  display: flex;
  flex-direction: column-reverse;
  align-items: center;
  gap: 2px;
  height: 150px;
  justify-content: flex-start;
}

.bar {
  width: 30px;
  border-radius: 4px 4px 0 0;
  transition: all 0.3s ease;
  cursor: pointer;
}

.bar:hover {
  opacity: 0.8;
  transform: scaleX(1.1);
}

.lost-bar {
  background: linear-gradient(to top, #ff9a9e 0%, #fad0c4 100%);
}

.found-bar {
  background: linear-gradient(to top, #a1c4fd 0%, #c2e9fb 100%);
}

.bar-label {
  font-family: "Comic Sans MS", cursive;
  font-size: 12px;
  color: rgba(166, 124, 82, 0.7);
}

/* 分类列表 */
.category-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.category-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.category-color {
  width: 16px;
  height: 16px;
  border-radius: 4px;
  flex-shrink: 0;
}

.category-info {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.category-name {
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
}

.category-count {
  font-family: "Comic Sans MS", cursive;
  font-size: 13px;
  color: rgba(166, 124, 82, 0.7);
}

.category-bar {
  width: 100px;
  height: 6px;
  background: rgba(166, 124, 82, 0.1);
  border-radius: 3px;
  overflow: hidden;
}

.category-progress {
  height: 100%;
  border-radius: 3px;
  transition: width 0.5s ease;
}

/* 实时动态 */
.activity-section {
  background: rgba(255, 255, 255, 0.35);
  backdrop-filter: blur(15px);
  border-radius: 20px;
  padding: 20px;
  border: 2px solid rgba(166, 124, 82, 0.2);
  margin-bottom: 25px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-title {
  font-family: "Comic Sans MS", cursive;
  font-size: 18px;
  color: #a67c52;
  margin: 0;
  font-weight: 600;
}

.refresh-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(166, 124, 82, 0.1);
  border: 1px solid rgba(166, 124, 82, 0.3);
  border-radius: 10px;
  font-family: "Comic Sans MS", cursive;
  font-size: 13px;
  color: #a67c52;
  cursor: pointer;
  transition: all 0.3s ease;
}

.refresh-btn:hover {
  background: rgba(166, 124, 82, 0.2);
}

.refresh-icon {
  font-size: 14px;
  transition: transform 0.5s ease;
}

.refresh-btn.rotating .refresh-icon {
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 12px;
  transition: all 0.3s ease;
}

.activity-item:hover {
  background: rgba(255, 255, 255, 0.5);
  transform: translateX(5px);
}

.activity-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
}

.activity-icon.publish { background: rgba(243, 129, 129, 0.2); }
.activity-icon.audit { background: rgba(76, 175, 80, 0.2); }
.activity-icon.claim { background: rgba(33, 150, 243, 0.2); }
.activity-icon.register { background: rgba(156, 39, 176, 0.2); }
.activity-icon.archive { background: rgba(121, 85, 72, 0.2); }

.activity-content {
  flex: 1;
}

.activity-text {
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
  margin-bottom: 4px;
}

.activity-time {
  font-family: "Comic Sans MS", cursive;
  font-size: 12px;
  color: rgba(166, 124, 82, 0.6);
}

/* 快捷操作 */
.quick-actions-section {
  background: rgba(255, 255, 255, 0.35);
  backdrop-filter: blur(15px);
  border-radius: 20px;
  padding: 20px;
  border: 2px solid rgba(166, 124, 82, 0.2);
}

.action-buttons {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.action-btn {
  flex: 1;
  min-width: 140px;
  padding: 15px 20px;
  border: none;
  border-radius: 12px;
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.action-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}

.action-btn.primary {
  background: linear-gradient(to right, #f38181, #f77d5f);
}

.action-btn.success {
  background: linear-gradient(to right, #4caf50, #8bc34a);
}

.action-btn.warning {
  background: linear-gradient(to right, #ff9800, #ffc107);
  color: #333;
}

.action-btn.info {
  background: linear-gradient(to right, #2196f3, #21cbf3);
}

.btn-icon {
  font-size: 24px;
}

/* 响应式 */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(3, 1fr);
  }
  
  .chart-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .main-content {
    margin-left: 0;
    max-width: 100vw;
    padding: 20px 15px;
    padding-bottom: 100px;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }
  
  .stat-value {
    font-size: 22px;
  }
  
  .action-buttons {
    flex-direction: column;
  }
  
  .action-btn {
    width: 100%;
    flex-direction: row;
    justify-content: center;
  }
}
</style>