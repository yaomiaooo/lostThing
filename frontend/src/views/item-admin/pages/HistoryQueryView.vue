<!-- src/views/item-admin/pages/HistoryQueryView.vue -->
<template>
  <div class="history-query-page">
    <!-- 背景 -->
    <div class="background-container">
      <div class="solid-background"></div>
    </div>

    <!-- 整体布局 -->
    <div class="layout-container">
      <!-- 左侧导航 -->
      <AdminNavigation 
        subtitle="历史查询"
        active-nav="历史查询"
        @logout="handleLogout"
      />

      <!-- 右侧主内容 -->
      <main class="main-content">
        <!-- 页面标题 -->
        <section class="page-header">
          <h1 class="page-title">审核历史查询</h1>
          <p class="page-subtitle">查看过往审核记录，支持多维度筛选</p>
        </section>

        <!-- 筛选区域 -->
        <section class="filter-section">
          <!-- 时间范围快捷选择 -->
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

          <!-- 其他筛选条件 -->
          <div class="filter-row">
            <select v-model="filterParams.status" class="filter-select" @change="loadHistory(1)">
              <option value="">全部审核结果</option>
              <option value="2">通过</option>
              <option value="5">驳回</option>
            </select>
            <select v-model="filterParams.itemCategory" class="filter-select" @change="loadHistory(1)">
              <option value="">全部信息类型</option>
              <option value="1">失物</option>
              <option value="2">招领</option>
            </select>
            <input 
              type="text" 
              v-model="filterParams.keyword" 
              class="filter-input" 
              placeholder="物品名称关键词"
              @keyup.enter="loadHistory(1)"
            />
            <button class="search-btn" @click="loadHistory(1)">
              🔍 查询
            </button>
            <button class="reset-btn" @click="resetFilters">
              ↻ 重置
            </button>
          </div>
        </section>

        <!-- 历史记录列表 -->
        <section class="list-section">
          <!-- 加载中 -->
          <div v-if="loading" class="loading-container">
            <div class="loading-spinner"></div>
            <div class="loading-text">加载历史记录中...</div>
          </div>

          <!-- 空状态 -->
          <div v-else-if="historyList.length === 0" class="empty-container">
            <div class="empty-icon">📭</div>
            <div class="empty-title">暂无审核记录</div>
            <div class="empty-desc">尝试调整筛选条件</div>
          </div>

          <!-- 数据表格 -->
          <div v-else class="table-container">
            <table class="data-table">
              <thead>
                <tr>
                  <th>审核时间</th>
                  <th>物品名称</th>
                  <th>信息类型</th>
                  <th>审核结果</th>
                  <th>驳回原因/备注</th>
                  <th>审核人</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="record in historyList" :key="record.historyId" class="table-row">
                  <td>{{ record.operateTime }}</td>
                  <td>
                    <span class="item-name">{{ record.itemName }}</span>
                  </td>
                  <td>
                    <span class="type-tag" :class="record.itemCategory === 1 ? 'lost-tag' : 'found-tag'">
                      {{ record.itemCategoryName }}
                    </span>
                  </td>
                  <td>
                    <span class="status-tag" :class="record.newStatus === 2 ? 'status-approved' : 'status-rejected'">
                      {{ record.newStatusName }}
                    </span>
                  </td>
                  <td>{{ record.reason || '-' }}</td>
                  <td>{{ record.operatorName }}</td>
                  <td>
                    <button class="view-detail-btn" @click="viewItemDetail(record.itemId)">查看物品</button>
                  </td>
                </tr>
              </tbody>
            </table>

            <!-- 分页 -->
            <div class="pagination">
              <button class="page-btn" :disabled="pagination.page === 1" @click="changePage(pagination.page - 1)">
                上一页
              </button>
              <span class="page-info">第 {{ pagination.page }} / {{ pagination.totalPages }} 页</span>
              <button class="page-btn" :disabled="pagination.page >= pagination.totalPages" @click="changePage(pagination.page + 1)">
                下一页
              </button>
            </div>
          </div>
        </section>
      </main>
    </div>

    <!-- 物品详情弹窗（可选，可复用其他页面的详情弹窗，此处简化直接跳转） -->
    <!-- 为简化，我们跳转到待审核页面的详情（但管理员不一定有权限查看物品详情，可考虑打开新页面或弹窗，这里先预留） -->
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import AdminNavigation from '../components/AdminNavigation.vue'

const router = useRouter()

/* ================= 数据状态 ================= */
const loading = ref(false)
const historyList = ref<any[]>([])

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

/* ================= 筛选参数 ================= */
const filterParams = reactive({
  startDate: '',
  endDate: '',
  status: '',
  itemCategory: '',
  keyword: ''
})

/* ================= 分页信息 ================= */
const pagination = reactive({
  page: 1,
  size: 10,
  total: 0,
  totalPages: 1
})

/* ================= 方法 ================= */
const changeDateRange = (range: string) => {
  currentRange.value = range
  if (range === 'custom') return

  const today = new Date()
  const todayStr = today.toISOString().split('T')[0]
  const tomorrow = new Date(today)
  tomorrow.setDate(today.getDate() + 1)
  const tomorrowStr = tomorrow.toISOString().split('T')[0]

  if (range === 'today') {
    // 查询今天到明天凌晨，确保包含今天的所有记录
    filterParams.startDate = todayStr
    filterParams.endDate = tomorrowStr
  } else if (range === 'week') {
    const start = new Date(today)
    start.setDate(today.getDate() - 7)
    filterParams.startDate = start.toISOString().split('T')[0]
    filterParams.endDate = tomorrowStr
  } else if (range === 'month') {
    const start = new Date(today)
    start.setMonth(today.getMonth() - 1)
    filterParams.startDate = start.toISOString().split('T')[0]
    filterParams.endDate = tomorrowStr
  }
  loadHistory(1)
}

const applyCustomRange = () => {
  if (customStartDate.value && customEndDate.value) {
    filterParams.startDate = customStartDate.value
    filterParams.endDate = customEndDate.value
    loadHistory(1)
  }
}

const resetFilters = () => {
  filterParams.status = ''
  filterParams.itemCategory = ''
  filterParams.keyword = ''
  currentRange.value = 'today'
  const today = new Date().toISOString().split('T')[0]
  const tomorrow = new Date()
  tomorrow.setDate(tomorrow.getDate() + 1)
  const tomorrowStr = tomorrow.toISOString().split('T')[0]
  
  // 查询今天到明天凌晨，确保包含今天的所有记录
  filterParams.startDate = today
  filterParams.endDate = tomorrowStr
  loadHistory(1)
}

/* ================= 加载审核历史 ================= */
const loadHistory = async (page = 1) => {
  loading.value = true
  pagination.page = page
  try {
    const params: any = {
      page,
      size: pagination.size,
      startDate: filterParams.startDate || undefined,
      endDate: filterParams.endDate || undefined,
      status: filterParams.status || undefined,
      itemCategory: filterParams.itemCategory || undefined,
      keyword: filterParams.keyword || undefined
    }

    const res = await axios.get('/api/item/audit/history', { params })
    if (res.data.code === 200) {
      const data = res.data.data
      historyList.value = data.list || []
      pagination.total = data.total || 0
      pagination.totalPages = Math.ceil(pagination.total / pagination.size)
    }
  } catch (error) {
    console.error('加载审核历史失败', error)
    // 模拟数据（开发时可删除）
    mockData()
  } finally {
    loading.value = false
  }
}

/* ================= 模拟数据（仅开发调试用） ================= */
const mockData = () => {
  historyList.value = [
    {
      historyId: 1,
      itemId: 101,
      itemName: '黑色钱包',
      itemCategory: 1,
      itemCategoryName: '失物',
      newStatus: 2,
      newStatusName: '已通过',
      reason: '',
      operatorName: '管理员A',
      operateTime: '2026-03-01 10:23:45'
    },
    {
      historyId: 2,
      itemId: 102,
      itemName: '校园卡',
      itemCategory: 2,
      itemCategoryName: '招领',
      newStatus: 5,
      newStatusName: '已驳回',
      reason: '照片不清晰',
      operatorName: '管理员B',
      operateTime: '2026-02-28 16:12:30'
    }
  ]
  pagination.total = 2
  pagination.totalPages = 1
}

/* ================= 分页切换 ================= */
const changePage = (page: number) => {
  if (page < 1 || page > pagination.totalPages) return
  loadHistory(page)
}

/* ================= 查看物品详情 ================= */
const viewItemDetail = (itemId: number) => {
  // 跳转到物品详情页（需要确认路由是否存在），或打开弹窗
  // 由于暂未实现物品详情页面，可先跳转到待审核页面的详情弹窗？或者新开页面
  // 这里简单使用 window.open 或 router.push，但需要后端支持
  // 根据实际路由调整，例如跳转到 /item-admin/items?itemId=xxx
  alert(`查看物品详情功能待完善，物品ID: ${itemId}`)
  // 实际可调用 router.push(`/item-admin/items?itemId=${itemId}`)
}

/* ================= 退出登录 ================= */
const handleLogout = () => {
  router.push('/login')
}

/* ================= 生命周期 ================= */
onMounted(() => {
  // 初始化日期为今日（包含完整时间段）
  const today = new Date()
  const todayStr = today.toISOString().split('T')[0]
  const tomorrow = new Date(today)
  tomorrow.setDate(today.getDate() + 1)
  const tomorrowStr = tomorrow.toISOString().split('T')[0]
  
  customStartDate.value = todayStr
  customEndDate.value = tomorrowStr
  filterParams.startDate = todayStr
  filterParams.endDate = tomorrowStr
  loadHistory()
})
</script>

<style scoped>
/* 基础布局 */
.history-query-page {
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

/* 筛选区域 */
.filter-section {
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(15px);
  border-radius: 12px;
  padding: 20px;
  border: 2px solid rgba(166, 124, 82, 0.2);
  margin-bottom: 20px;
}

.date-range-buttons {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 15px;
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
  margin-bottom: 15px;
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

.filter-row {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  align-items: center;
}

.filter-select, .filter-input {
  padding: 10px 15px;
  border: 1.6px solid rgba(166, 124, 82, 0.4);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.4);
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
  outline: none;
}

.filter-input {
  flex: 1;
  min-width: 200px;
}

.search-btn, .reset-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 10px;
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.search-btn {
  background: linear-gradient(to right, #f38181, #f77d5f);
  color: white;
}

.reset-btn {
  background: rgba(166, 124, 82, 0.1);
  color: #a67c52;
  border: 1px solid rgba(166, 124, 82, 0.3);
}

/* 列表区域 */
.list-section {
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(15px);
  border-radius: 20px;
  padding: 20px;
  border: 2px solid rgba(166, 124, 82, 0.2);
  min-height: 400px;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 0;
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

.empty-container {
  text-align: center;
  padding: 80px 0;
}

.empty-icon { font-size: 64px; margin-bottom: 20px; }
.empty-title { font-size: 24px; color: #a67c52; margin-bottom: 12px; }
.empty-desc { font-size: 16px; color: rgba(166, 124, 82, 0.7); }

/* 表格 */
.table-container {
  overflow-x: auto;
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
  padding: 15px 12px;
  border-bottom: 1px solid rgba(166, 124, 82, 0.1);
  font-size: 14px;
  color: rgba(166, 124, 82, 0.9);
  vertical-align: middle;
}

.table-row:hover {
  background: rgba(255, 255, 255, 0.3);
}

.item-name {
  font-weight: 600;
  color: #a67c52;
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

.view-detail-btn {
  padding: 6px 12px;
  border: 1px solid rgba(166, 124, 82, 0.4);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.3);
  font-family: "Comic Sans MS", cursive;
  font-size: 12px;
  color: #a67c52;
  cursor: pointer;
  transition: all 0.3s ease;
}

.view-detail-btn:hover {
  background: rgba(166, 124, 82, 0.2);
  transform: translateY(-2px);
}

/* 分页 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  margin-top: 25px;
  padding-top: 20px;
  border-top: 1px solid rgba(166, 124, 82, 0.1);
}

.page-btn {
  padding: 10px 20px;
  border: 1.6px solid rgba(166, 124, 82, 0.4);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.4);
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
  cursor: pointer;
  transition: all 0.3s ease;
}
.page-btn:hover:not(:disabled) {
  border-color: rgba(243, 129, 129, 0.7);
  background: rgba(255, 255, 255, 0.6);
}
.page-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.page-info { font-size: 14px; color: rgba(166, 124, 82, 0.8); }

/* 响应式 */
@media (max-width: 768px) {
  .main-content {
    margin-left: 0;
    max-width: 100vw;
    padding: 20px 15px;
    padding-bottom: 100px;
  }
  .filter-row {
    flex-direction: column;
    align-items: stretch;
  }
  .filter-input { width: auto; }
}
</style>