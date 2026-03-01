<!-- src/views/item-admin/pages/StatisticsView.vue -->
<template>
  <div class="statistics-page">
    <!-- 背景 -->
    <div class="background-container">
      <div class="solid-background"></div>
    </div>

    <!-- 整体布局 -->
    <div class="layout-container">
      <!-- 左侧导航 -->
      <AdminNavigation 
        subtitle="数据统计"
        active-nav="数据统计"
        @logout="handleLogout"
      />

      <!-- 右侧主内容 -->
      <main class="main-content">
        <!-- 页面标题 -->
        <section class="page-header">
          <h1 class="page-title">📊 数据统计</h1>
          <p class="page-subtitle">查看个人审核工作量与整体趋势</p>
        </section>

        <!-- 时间范围选择 -->
        <section class="date-range-section">
          <div class="date-range-buttons">
            <button 
              v-for="range in dateRanges" 
              :key="range.value"
              class="date-btn"
              :class="{ active: currentRange === range.value }"
              @click="changeDateRange(range.value)"
            >
              {{ range.label }}
            </button>
          </div>
          <div class="custom-range" v-if="currentRange === 'custom'">
            <input type="date" v-model="customStartDate" class="date-input" />
            <span>至</span>
            <input type="date" v-model="customEndDate" class="date-input" />
            <button class="apply-btn" @click="applyCustomRange">应用</button>
          </div>
        </section>

        <!-- 统计卡片 -->
        <section class="stats-section">
          <div class="stats-grid">
            <div class="stat-card">
              <div class="stat-icon">📋</div>
              <div class="stat-value">{{ overview.totalProcessed }}</div>
              <div class="stat-label">总处理数</div>
            </div>
            <div class="stat-card">
              <div class="stat-icon">✅</div>
              <div class="stat-value">{{ overview.approved }}</div>
              <div class="stat-label">通过数</div>
            </div>
            <div class="stat-card">
              <div class="stat-icon">❌</div>
              <div class="stat-value">{{ overview.rejected }}</div>
              <div class="stat-label">驳回数</div>
            </div>
            <div class="stat-card">
              <div class="stat-icon">⏱️</div>
              <div class="stat-value">{{ overview.avgTime }}分钟</div>
              <div class="stat-label">平均处理时长</div>
            </div>
          </div>
        </section>

        <!-- 图表区域（模拟） -->
        <section class="chart-section">
          <h2 class="section-title">每日审核趋势</h2>
          <div class="chart-placeholder">
            <!-- 这里可以集成 ECharts 等组件，暂时用模拟条状图代替 -->
            <div class="bar-chart">
              <div 
                v-for="(day, index) in trendData" 
                :key="index"
                class="bar-item"
                :style="{ height: day.value * 3 + 'px' }"
              >
                <span class="bar-label">{{ day.date }}</span>
              </div>
            </div>
          </div>
        </section>

        <!-- 个人审核明细 -->
        <section class="detail-section">
          <h2 class="section-title">个人审核明细</h2>
          <div class="toolbar-section" style="padding: 10px 0;">
            <div class="filter-group">
              <select v-model="detailFilter.status" class="filter-select" @change="loadAuditHistory">
                <option value="">全部结果</option>
                <option value="2">通过</option>
                <option value="5">驳回</option>
              </select>
            </div>
          </div>
          <div class="table-container">
            <table class="data-table">
              <thead>
                <tr>
                  <th>时间</th>
                  <th>物品名称</th>
                  <th>类型</th>
                  <th>审核结果</th>
                  <th>驳回原因</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="record in auditList" :key="record.id" class="table-row">
                  <td>{{ record.auditTime }}</td>
                  <td>{{ record.itemName }}</td>
                  <td>
                    <span class="type-tag" :class="record.itemCategory === 1 ? 'lost-tag' : 'found-tag'">
                      {{ record.itemCategory === 1 ? '失物' : '招领' }}
                    </span>
                  </td>
                  <td>
                    <span class="status-tag" :class="record.status === 2 ? 'status-approved' : 'status-rejected'">
                      {{ record.status === 2 ? '通过' : '驳回' }}
                    </span>
                  </td>
                  <td>{{ record.rejectReason || '-' }}</td>
                </tr>
                <tr v-if="auditList.length === 0">
                  <td colspan="5" class="empty-table">暂无审核记录</td>
                </tr>
              </tbody>
            </table>
          </div>
          <!-- 导出按钮 -->
          <div class="export-section">
            <button class="export-btn" @click="exportData">
              📥 导出统计报表
            </button>
          </div>
        </section>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import AdminNavigation from '../components/AdminNavigation.vue'

const router = useRouter()

/* ================= 日期范围 ================= */
const dateRanges = [
  { label: '今日', value: 'today' },
  { label: '本周', value: 'week' },
  { label: '本月', value: 'month' },
  { label: '自定义', value: 'custom' }
]
const currentRange = ref('today')
const customStartDate = ref('')
const customEndDate = ref('')

const changeDateRange = (range: string) => {
  currentRange.value = range
  if (range !== 'custom') {
    loadStatistics()
    loadAuditHistory()
  }
}
const applyCustomRange = () => {
  if (customStartDate.value && customEndDate.value) {
    loadStatistics()
    loadAuditHistory()
  }
}

/* ================= 统计数据 ================= */
const overview = reactive({
  totalProcessed: 0,
  approved: 0,
  rejected: 0,
  avgTime: 0
})

// 模拟趋势数据
const trendData = ref([
  { date: '03-01', value: 5 },
  { date: '03-02', value: 8 },
  { date: '03-03', value: 3 },
  { date: '03-04', value: 10 },
  { date: '03-05', value: 7 },
  { date: '03-06', value: 4 },
  { date: '03-07', value: 6 }
])

/* ================= 审核明细 ================= */
const auditList = ref<any[]>([])
const detailFilter = reactive({
  status: ''
})

const loadStatistics = async () => {
  try {
    const params: any = {}
    if (currentRange.value === 'today') {
      params.startDate = new Date().toISOString().split('T')[0]
      params.endDate = params.startDate
    } else if (currentRange.value === 'week') {
      const end = new Date()
      const start = new Date()
      start.setDate(end.getDate() - 7)
      params.startDate = start.toISOString().split('T')[0]
      params.endDate = end.toISOString().split('T')[0]
    } else if (currentRange.value === 'month') {
      const end = new Date()
      const start = new Date()
      start.setMonth(end.getMonth() - 1)
      params.startDate = start.toISOString().split('T')[0]
      params.endDate = end.toISOString().split('T')[0]
    } else if (currentRange.value === 'custom') {
      params.startDate = customStartDate.value
      params.endDate = customEndDate.value
    }

    const res = await axios.get('/api/item/statistics/overview', { params })
    if (res.data.code === 200) {
      const data = res.data.data
      overview.totalProcessed = data.totalProcessed || 0
      overview.approved = data.approved || 0
      overview.rejected = data.rejected || 0
      overview.avgTime = data.avgTime || 0
    }
  } catch (error) {
    console.error('加载统计数据失败', error)
    // 模拟数据
    overview.totalProcessed = 156
    overview.approved = 132
    overview.rejected = 24
    overview.avgTime = 8
  }
}

const loadAuditHistory = async () => {
  try {
    const params: any = {
      page: 1,
      size: 20,
      status: detailFilter.status || undefined
    }
    if (currentRange.value === 'today') {
      params.startDate = new Date().toISOString().split('T')[0]
      params.endDate = params.startDate
    } else if (currentRange.value === 'week') {
      const end = new Date()
      const start = new Date()
      start.setDate(end.getDate() - 7)
      params.startDate = start.toISOString().split('T')[0]
      params.endDate = end.toISOString().split('T')[0]
    } else if (currentRange.value === 'month') {
      const end = new Date()
      const start = new Date()
      start.setMonth(end.getMonth() - 1)
      params.startDate = start.toISOString().split('T')[0]
      params.endDate = end.toISOString().split('T')[0]
    } else if (currentRange.value === 'custom') {
      params.startDate = customStartDate.value
      params.endDate = customEndDate.value
    }

    const res = await axios.get('/api/item/audit/history', { params })
    if (res.data.code === 200) {
      auditList.value = res.data.data.list || []
    }
  } catch (error) {
    console.error('加载审核历史失败', error)
    // 模拟数据
    auditList.value = [
      { id: 1, auditTime: '2026-03-01 10:23', itemName: '黑色钱包', itemCategory: 1, status: 2, rejectReason: '' },
      { id: 2, auditTime: '2026-03-01 09:15', itemName: '校园卡', itemCategory: 2, status: 5, rejectReason: '照片模糊' },
      { id: 3, auditTime: '2026-02-28 16:40', itemName: '水杯', itemCategory: 1, status: 2, rejectReason: '' }
    ]
  }
}

/* ================= 导出 ================= */
const exportData = () => {
  // 调用导出接口
  window.open('/api/item/statistics/export?format=csv', '_blank')
}

/* ================= 退出登录 ================= */
const handleLogout = () => {
  router.push('/login')
}

/* ================= 生命周期 ================= */
onMounted(() => {
  // 初始化日期
  const today = new Date().toISOString().split('T')[0]
  customStartDate.value = today
  customEndDate.value = today
  loadStatistics()
  loadAuditHistory()
})
</script>

<style scoped>
/* 基础布局 */
.statistics-page {
  width: 100vw;
  min-height: 100vh;
  position: relative;
  overflow-x: hidden;
}

.background-container {
  position: fixed;
  top: 0; left: 0; width: 100%; height: 100%;
  z-index: 1;
  overflow: hidden;
}

.solid-background {
  position: absolute;
  top: 0; left: 0; width: 100%; height: 100%;
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

/* 日期范围 */
.date-range-section {
  margin-bottom: 25px;
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(15px);
  border-radius: 12px;
  padding: 15px 20px;
  border: 2px solid rgba(166, 124, 82, 0.2);
}

.date-range-buttons {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 10px;
}

.date-btn {
  padding: 8px 20px;
  border: 1.6px solid rgba(166, 124, 82, 0.4);
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.4);
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
  cursor: pointer;
  transition: all 0.3s ease;
}

.date-btn.active {
  background: linear-gradient(to right, #f38181, #f77d5f);
  color: white;
  border-color: transparent;
}

.custom-range {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 10px;
  flex-wrap: wrap;
}

.date-input {
  padding: 8px 12px;
  border: 1.6px solid rgba(166, 124, 82, 0.4);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.4);
  font-family: "Comic Sans MS", cursive;
  color: #a67c52;
}

.apply-btn {
  padding: 8px 20px;
  border: none;
  border-radius: 8px;
  background: linear-gradient(to right, #f38181, #f77d5f);
  color: white;
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

/* 统计卡片 */
.stats-section {
  margin-bottom: 30px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.stat-card {
  background: rgba(255, 255, 255, 0.35);
  backdrop-filter: blur(15px);
  border-radius: 16px;
  padding: 20px;
  border: 2px solid rgba(166, 124, 82, 0.2);
  text-align: center;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.stat-icon { font-size: 32px; margin-bottom: 10px; }
.stat-value { font-size: 28px; color: #a67c52; font-weight: 700; margin-bottom: 5px; }
.stat-label { font-size: 14px; color: rgba(166, 124, 82, 0.7); }

/* 图表区域 */
.chart-section {
  margin-bottom: 30px;
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(15px);
  border-radius: 20px;
  padding: 20px;
  border: 2px solid rgba(166, 124, 82, 0.2);
}

.section-title {
  font-family: "Comic Sans MS", cursive;
  font-size: 18px;
  color: #a67c52;
  margin: 0 0 20px 0;
  padding-left: 10px;
  border-left: 4px solid #f38181;
}

.chart-placeholder {
  height: 200px;
  display: flex;
  align-items: flex-end;
  justify-content: center;
}

.bar-chart {
  display: flex;
  align-items: flex-end;
  gap: 15px;
  height: 150px;
}

.bar-item {
  width: 30px;
  background: linear-gradient(to top, #f38181, #f77d5f);
  border-radius: 6px 6px 0 0;
  position: relative;
  min-height: 4px;
}

.bar-label {
  position: absolute;
  bottom: -20px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 11px;
  color: rgba(166, 124, 82, 0.7);
  white-space: nowrap;
}

/* 明细表格 */
.detail-section {
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(15px);
  border-radius: 20px;
  padding: 20px;
  border: 2px solid rgba(166, 124, 82, 0.2);
}

.table-container {
  overflow-x: auto;
  margin-bottom: 20px;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-family: "Comic Sans MS", cursive;
}

.data-table th {
  background: rgba(166, 124, 82, 0.1);
  padding: 15px 12px;
  text-align: left;
  font-size: 14px;
  color: #a67c52;
  font-weight: 600;
  border-bottom: 2px solid rgba(166, 124, 82, 0.2);
  white-space: nowrap;
}

.data-table td {
  padding: 12px;
  border-bottom: 1px solid rgba(166, 124, 82, 0.1);
  font-size: 14px;
  color: rgba(166, 124, 82, 0.9);
}

.table-row:hover {
  background: rgba(255, 255, 255, 0.3);
}

.type-tag {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  color: white;
}
.lost-tag { background: linear-gradient(135deg, #ff9a9e 0%, #fad0c4 100%); }
.found-tag { background: linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%); }

.status-tag {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
}
.status-approved { background: #4caf50; color: white; }
.status-rejected { background: #f44336; color: white; }

.empty-table {
  text-align: center;
  padding: 40px;
  color: rgba(166, 124, 82, 0.5);
}

.export-section {
  text-align: right;
}

.export-btn {
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

.export-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(243, 129, 129, 0.4);
}

/* 响应式 */
@media (max-width: 768px) {
  .main-content {
    margin-left: 0;
    max-width: 100vw;
    padding: 20px 15px;
    padding-bottom: 100px;
  }
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .custom-range { flex-direction: column; align-items: stretch; }
  .date-input { width: 100%; }
}
</style>