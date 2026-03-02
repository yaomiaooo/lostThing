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

    <!-- 物品详情弹窗 -->
    <div v-if="showDetailModal" class="modal-overlay" @click.self="closeDetailModal">
      <div class="detail-modal">
        <div class="modal-header">
          <h3 class="modal-title">物品详情</h3>
          <button class="modal-close" @click="closeDetailModal">×</button>
        </div>
        <div class="modal-body">
          <div class="detail-content" v-if="currentItem">
            <!-- 图片展示 -->
            <div class="detail-images" v-if="currentItemImages.length > 0">
              <div class="image-main">
                <img 
                  :src="currentItemImages[currentImageIndex]" 
                  class="main-image" 
                  @click="previewImage(currentItemImages[currentImageIndex])"
                />
              </div>
              <div class="image-thumbs" v-if="currentItemImages.length > 1">
                <img 
                  v-for="(img, idx) in currentItemImages" 
                  :key="idx"
                  :src="img" 
                  class="thumb" 
                  :class="{ active: idx === currentImageIndex }"
                  @click="currentImageIndex = idx"
                />
              </div>
            </div>
            
            <!-- 基本信息 -->
            <div class="detail-info">
              <div class="info-row">
                <span class="info-label">物品名称：</span>
                <span class="info-value">{{ currentItem.name }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">物品类型：</span>
                <span class="info-value">{{ currentItem.itemTypeName }}（{{ currentItem.itemCategory === 1 ? '失物' : '招领' }}）</span>
              </div>
              <div class="info-row" v-if="currentItem.happenTime">
                <span class="info-label">发生时间：</span>
                <span class="info-value">{{ currentItem.happenTime }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">地点：</span>
                <span class="info-value">{{ getLocationCampus(currentItem) }} {{ currentItem.locationName }} {{ currentItem.locationDetail }}</span>
              </div>
              <div class="info-row" v-if="currentItem.pickupLocation">
                <span class="info-label">领取地点：</span>
                <span class="info-value">{{ currentItem.pickupLocation }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">特征描述：</span>
                <span class="info-value description">{{ currentItem.feature }}</span>
              </div>
              <div class="info-row" v-if="currentItem.rewardAmount > 0">
                <span class="info-label">悬赏金额：</span>
                <span class="info-value reward">¥{{ currentItem.rewardAmount }} {{ currentItem.rewardDesc }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">联系人：</span>
                <span class="info-value">{{ currentItem.contactName }} {{ currentItem.contactPhone }}</span>
              </div>
              <div class="info-row" v-if="currentItem.createTime">
                <span class="info-label">发布时间：</span>
                <span class="info-value">{{ currentItem.createTime }}</span>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="modal-btn cancel-btn" @click="closeDetailModal">关闭</button>
        </div>
      </div>
    </div>

    <!-- 图片预览 -->
    <div v-if="previewImageUrl" class="image-preview-overlay" @click.self="closeImagePreview">
      <img :src="previewImageUrl" class="preview-large" />
      <button class="preview-close" @click="closeImagePreview">×</button>
    </div>
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

/* ================= 弹窗状态 ================= */
const showDetailModal = ref(false)
const currentItem = ref<any>(null)
const currentItemImages = ref<string[]>([])
const currentImageIndex = ref(0)
const previewImageUrl = ref('')

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

  const now = new Date()
  // 创建新的日期对象，避免修改原对象
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  
  const formatDateTime = (date: Date, isEnd: boolean = false) => {
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    // 结束时间需要包含整天，设为 23:59:59
    const time = isEnd ? '23:59:59' : '00:00:00'
    return `${year}-${month}-${day} ${time}`
  }

  if (range === 'today') {
    // 今日：00:00:00 到 23:59:59
    filterParams.startDate = formatDateTime(today, false)
    filterParams.endDate = formatDateTime(today, true)
  } else if (range === 'week') {
    // 本周（最近7天）：6天前 00:00:00 到 今天 23:59:59
    const start = new Date(today)
    start.setDate(today.getDate() - 6)
    filterParams.startDate = formatDateTime(start, false)
    filterParams.endDate = formatDateTime(today, true)
  } else if (range === 'month') {
    // 本月（最近30天）：29天前 00:00:00 到 今天 23:59:59
    const start = new Date(today)
    start.setDate(today.getDate() - 29)
    filterParams.startDate = formatDateTime(start, false)
    filterParams.endDate = formatDateTime(today, true)
  }
  loadHistory(1)
}

// 自定义日期范围也需要修复
const applyCustomRange = () => {
  if (customStartDate.value && customEndDate.value) {
    // 开始日期 00:00:00，结束日期 23:59:59
    filterParams.startDate = `${customStartDate.value} 00:00:00`
    filterParams.endDate = `${customEndDate.value} 23:59:59`
    loadHistory(1)
  }
}

// 重置时也要用完整时间格式
const resetFilters = () => {
  filterParams.status = ''
  filterParams.itemCategory = ''
  filterParams.keyword = ''
  currentRange.value = 'today'
  
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const formatDate = (date: Date) => {
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    return `${year}-${month}-${day}`
  }
  
  const todayStr = formatDate(today)
  customStartDate.value = todayStr
  customEndDate.value = todayStr
  filterParams.startDate = `${todayStr} 00:00:00`
  filterParams.endDate = `${todayStr} 23:59:59`
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
const viewItemDetail = async (itemId: number) => {
  currentItem.value = { itemId }
  currentImageIndex.value = 0
  
  // 加载物品详情获取图片
  try {
    const res = await axios.get('/api/item/detail', {
      params: { itemId }
    })
    
    if (res.data.code === 200) {
      const detail = res.data.data
      currentItem.value = detail.item
      
      // 处理图片
      if (detail.images && detail.images.length > 0) {
        currentItemImages.value = detail.images.map((img: any) => img.url)
      } else if (currentItem.value.firstImageUrl) {
        currentItemImages.value = [currentItem.value.firstImageUrl]
      } else {
        currentItemImages.value = []
      }
    }
  } catch (error) {
    console.error('加载详情失败:', error)
    currentItemImages.value = []
  }
  
  showDetailModal.value = true
}

const closeDetailModal = () => {
  showDetailModal.value = false
  currentItem.value = null
  currentItemImages.value = []
}

/* ================= 图片预览 ================= */
const previewImage = (url: string | null) => {
  if (!url) return
  previewImageUrl.value = url
}

const closeImagePreview = () => {
  previewImageUrl.value = ''
}

/* ================= 地点解析函数 ================= */
const getLocationCampus = (item: any) => {
  const locationId = item.locationId || 0
  
  // 根据locationId的前缀判断校区
  // 1xxxx = 朝晖校区, 2xxxx = 屏峰校区, 3xxxx = 莫干山校区, 4xxxx = 西湖校区
  const idStr = String(locationId)
  
  if (idStr.startsWith('1')) {
    return '朝晖校区'
  } else if (idStr.startsWith('2')) {
    return '屏峰校区'
  } else if (idStr.startsWith('3')) {
    return '莫干山校区'
  } else if (idStr.startsWith('4')) {
    return '西湖校区'
  }
  
  // 如果无法从locationId判断，尝试从locationName中提取
  const locationName = item.locationName || ''
  const campusPatterns = ['屏峰校区', '朝晖校区', '莫干山校区', '西湖校区']
  
  for (const campus of campusPatterns) {
    if (locationName.includes(campus)) {
      return campus
    }
  }
  
  return '未知校区'
}

/* ================= 退出登录 ================= */
const handleLogout = () => {
  router.push('/login')
}

/* ================= 生命周期 ================= */
onMounted(() => {
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const formatDate = (date: Date) => {
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    return `${year}-${month}-${day}`
  }
  
  const todayStr = formatDate(today)
  customStartDate.value = todayStr
  customEndDate.value = todayStr
  filterParams.startDate = `${todayStr} 00:00:00`
  filterParams.endDate = `${todayStr} 23:59:59`
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

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(5px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid rgba(166, 124, 82, 0.1);
}

.modal-title {
  font-family: "Comic Sans MS", cursive;
  font-size: 20px;
  color: #a67c52;
  margin: 0;
  font-weight: 600;
}

.modal-close {
  background: none;
  border: none;
  font-size: 24px;
  color: rgba(166, 124, 82, 0.6);
  cursor: pointer;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.3s ease;
}

.modal-close:hover {
  background: rgba(166, 124, 82, 0.1);
  color: #a67c52;
}

.modal-body {
  padding: 20px;
  max-height: 60vh;
  overflow-y: auto;
}

.modal-footer {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  padding: 20px;
  border-top: 1px solid rgba(166, 124, 82, 0.1);
}

.modal-btn {
  padding: 12px 24px;
  border: none;
  border-radius: 10px;
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.cancel-btn {
  background: rgba(166, 124, 82, 0.1);
  color: #a67c52;
  border: 1px solid rgba(166, 124, 82, 0.3);
}

.cancel-btn:hover {
  background: rgba(166, 124, 82, 0.2);
}

/* 详情弹窗 */
.detail-modal {
  background: white;
  border-radius: 20px;
  width: 90%;
  max-width: 700px;
  max-height: 90vh;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.detail-content {
  display: flex;
  gap: 20px;
}

.detail-images {
  flex: 0 0 300px;
}

.image-main {
  width: 100%;
  height: 300px;
  border-radius: 12px;
  overflow: hidden;
  background: rgba(166, 124, 82, 0.1);
  margin-bottom: 12px;
}

.main-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-thumbs {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.thumb {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  object-fit: cover;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.3s ease;
}

.thumb.active {
  border-color: rgba(243, 129, 129, 0.7);
}

.thumb:hover {
  transform: scale(1.05);
}

.detail-info {
  flex: 1;
}

.info-row {
  margin-bottom: 15px;
}

.info-label {
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: rgba(166, 124, 82, 0.7);
  display: block;
  margin-bottom: 4px;
}

.info-value {
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
  word-break: break-word;
}

.info-value.description {
  line-height: 1.5;
}

.info-value.reward {
  color: #f44336;
  font-weight: 500;
}

/* 图片预览覆盖层 */
.image-preview-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.preview-large {
  max-width: 90%;
  max-height: 90%;
  object-fit: contain;
  border-radius: 8px;
}

.preview-close {
  position: absolute;
  top: 20px;
  right: 20px;
  width: 40px;
  height: 40px;
  border: none;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  font-size: 24px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.preview-close:hover {
  background: rgba(255, 255, 255, 0.3);
}

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
  
  .detail-content {
    flex-direction: column;
  }
  
  .detail-images {
    flex: 1;
  }
}
</style>