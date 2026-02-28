<template>
  <div class="audit-items-view">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1 class="page-title">审核发布信息</h1>
      <p class="page-subtitle">查看待审核的失物/招领信息，进行审核操作</p>
    </div>

    <!-- 筛选工具栏 -->
    <div class="filter-toolbar">
      <div class="filter-group">
        <label class="filter-label">信息类型：</label>
        <select v-model="filterParams.itemCategory" class="filter-select">
          <option value="">全部</option>
          <option value="1">失物信息</option>
          <option value="2">招领信息</option>
        </select>
      </div>
      
      <div class="filter-group">
        <label class="filter-label">状态：</label>
        <select v-model="filterParams.status" class="filter-select">
          <option value="">全部</option>
          <option value="1">待审核</option>
          <option value="2">已通过</option>
          <option value="5">已驳回</option>
        </select>
      </div>
      
      <div class="filter-group">
        <label class="filter-label">时间范围：</label>
        <input 
          v-model="filterParams.startDate" 
          type="date" 
          class="filter-input"
          placeholder="开始日期"
        >
        <span class="date-separator">至</span>
        <input 
          v-model="filterParams.endDate" 
          type="date" 
          class="filter-input"
          placeholder="结束日期"
        >
      </div>
      
      <button class="search-btn" @click="loadItems">
        <span class="search-icon">🔍</span>
        搜索
      </button>
      
      <button class="reset-btn" @click="resetFilters">重置</button>
    </div>

    <!-- 数据统计 -->
    <div class="stats-cards">
      <div class="stat-card">
        <div class="stat-value">{{ stats.pendingCount }}</div>
        <div class="stat-label">待审核</div>
      </div>
      <div class="stat-card approved">
        <div class="stat-value">{{ stats.approvedCount }}</div>
        <div class="stat-label">已通过</div>
      </div>
      <div class="stat-card rejected">
        <div class="stat-value">{{ stats.rejectedCount }}</div>
        <div class="stat-label">已驳回</div>
      </div>
      <div class="stat-card total">
        <div class="stat-value">{{ stats.totalCount }}</div>
        <div class="stat-label">总计</div>
      </div>
    </div>

    <!-- 物品列表 -->
    <div class="items-container">
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <div class="loading-text">加载中...</div>
      </div>
      
      <div v-else-if="items.length === 0" class="empty-state">
        <div class="empty-icon">📭</div>
        <div class="empty-text">暂无待审核信息</div>
      </div>
      
      <div v-else class="items-list">
        <div 
          v-for="item in items" 
          :key="item.id"
          class="item-card"
          :class="{ 
            'pending': item.currentStatus === 1,
            'approved': item.currentStatus === 2,
            'rejected': item.currentStatus === 5
          }"
        >
          <!-- 物品图片 -->
          <div class="item-image">
            <img 
              v-if="item.firstImageUrl" 
              :src="item.firstImageUrl" 
              :alt="item.name"
              @error="handleImageError"
            >
            <div v-else class="no-image">
              <span class="no-image-icon">📷</span>
              <span class="no-image-text">暂无图片</span>
            </div>
          </div>
          
          <!-- 物品信息 -->
          <div class="item-info">
            <div class="item-header">
              <h3 class="item-name">{{ item.name }}</h3>
              <span class="item-status" :class="getStatusClass(item.currentStatus)">
                {{ getStatusText(item.currentStatus) }}
              </span>
            </div>
            
            <div class="item-details">
              <div class="detail-item">
                <span class="detail-label">类型：</span>
                <span class="detail-value">{{ item.itemCategory === 1 ? '失物' : '招领' }}</span>
              </div>
              
              <div class="detail-item">
                <span class="detail-label">地点：</span>
                <span class="detail-value">{{ item.locationName }} {{ item.locationDetail || '' }}</span>
              </div>
              
              <div class="detail-item">
                <span class="detail-label">时间：</span>
                <span class="detail-value">{{ formatTime(item.happenTime) }}</span>
              </div>
              
              <div class="detail-item">
                <span class="detail-label">特征：</span>
                <span class="detail-value feature-text">{{ item.feature }}</span>
              </div>
              
              <div v-if="item.rewardAmount > 0" class="detail-item">
                <span class="detail-label">悬赏：</span>
                <span class="detail-value reward">￥{{ item.rewardAmount.toFixed(2) }}</span>
              </div>
            </div>
            
            <!-- 审核操作 -->
            <div class="item-actions">
              <button 
                v-if="item.currentStatus === 1"
                class="action-btn approve-btn"
                @click="openAuditDialog(item, 'approve')"
              >
                <span class="btn-icon">✅</span>
                通过
              </button>
              
              <button 
                v-if="item.currentStatus === 1"
                class="action-btn reject-btn"
                @click="openAuditDialog(item, 'reject')"
              >
                <span class="btn-icon">❌</span>
                驳回
              </button>
              
              <button 
                class="action-btn detail-btn"
                @click="viewItemDetail(item)"
              >
                <span class="btn-icon">👁️</span>
                查看详情
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 分页 -->
      <div v-if="items.length > 0" class="pagination">
        <button 
          :disabled="currentPage === 1"
          @click="changePage(currentPage - 1)"
          class="page-btn"
        >
          上一页
        </button>
        
        <span class="page-info">
          第 {{ currentPage }} 页，共 {{ totalPages }} 页
        </span>
        
        <button 
          :disabled="currentPage === totalPages"
          @click="changePage(currentPage + 1)"
          class="page-btn"
        >
          下一页
        </button>
      </div>
    </div>

    <!-- 审核弹窗 -->
    <AuditDialog 
      v-if="showAuditDialog"
      :item="currentItem"
      :audit-type="auditType"
      @confirm="handleAuditConfirm"
      @cancel="closeAuditDialog"
    />
    
    <!-- 详情弹窗 -->
    <ItemDetailDialog 
      v-if="showDetailDialog"
      :item="currentItem"
      @close="closeDetailDialog"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import request from '@/utils/request'
import AuditDialog from './components/AuditDialog.vue'
import ItemDetailDialog from './components/ItemDetailDialog.vue'

// 筛选参数
const filterParams = reactive({
  itemCategory: '',
  status: '',
  startDate: '',
  endDate: ''
})

// 分页参数
const currentPage = ref(1)
const pageSize = 10
const totalPages = ref(1)

// 数据
const items = ref<any[]>([])
const loading = ref(false)

// 统计信息
const stats = reactive({
  pendingCount: 0,
  approvedCount: 0,
  rejectedCount: 0,
  totalCount: 0
})

// 弹窗控制
const showAuditDialog = ref(false)
const showDetailDialog = ref(false)
const currentItem = ref<any>(null)
const auditType = ref<'approve' | 'reject'>('approve')

// 加载物品列表
const loadItems = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      size: pageSize,
      ...filterParams
    }
    
    const response = await request.get('/item/admin/list', { params })
    
    if (response.code === 200) {
      items.value = response.data.list || []
      totalPages.value = Math.ceil(response.data.total / pageSize)
      
      // 更新统计信息
      updateStats()
    }
  } catch (error) {
    console.error('加载物品列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 更新统计信息
const updateStats = () => {
  stats.pendingCount = items.value.filter(item => item.currentStatus === 1).length
  stats.approvedCount = items.value.filter(item => item.currentStatus === 2).length
  stats.rejectedCount = items.value.filter(item => item.currentStatus === 5).length
  stats.totalCount = items.value.length
}

// 重置筛选
const resetFilters = () => {
  filterParams.itemCategory = ''
  filterParams.status = ''
  filterParams.startDate = ''
  filterParams.endDate = ''
  currentPage.value = 1
  loadItems()
}

// 分页
const changePage = (page: number) => {
  currentPage.value = page
  loadItems()
}

// 获取状态文本
const getStatusText = (status: number) => {
  const statusMap: Record<number, string> = {
    1: '待审核',
    2: '已通过',
    5: '已驳回'
  }
  return statusMap[status] || '未知状态'
}

// 获取状态样式类
const getStatusClass = (status: number) => {
  const classMap: Record<number, string> = {
    1: 'status-pending',
    2: 'status-approved',
    5: 'status-rejected'
  }
  return classMap[status] || ''
}

// 格式化时间
const formatTime = (time: string) => {
  return new Date(time).toLocaleString('zh-CN')
}

// 图片加载失败处理
const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  img.style.display = 'none'
  img.parentElement?.querySelector('.no-image')?.classList.remove('hidden')
}

// 打开审核弹窗
const openAuditDialog = (item: any, type: 'approve' | 'reject') => {
  currentItem.value = item
  auditType.value = type
  showAuditDialog.value = true
}

// 关闭审核弹窗
const closeAuditDialog = () => {
  showAuditDialog.value = false
  currentItem.value = null
}

// 处理审核确认
const handleAuditConfirm = async (data: any) => {
  try {
    const response = await request.post('/item/audit', {
      itemId: data.itemId,
      status: data.status,
      rejectReason: data.rejectReason || ''
    })
    
    if (response.code === 200) {
      // 重新加载列表
      loadItems()
    }
  } catch (error) {
    console.error('审核操作失败:', error)
  }
}

// 查看详情
const viewItemDetail = (item: any) => {
  currentItem.value = item
  showDetailDialog.value = true
}

// 关闭详情弹窗
const closeDetailDialog = () => {
  showDetailDialog.value = false
  currentItem.value = null
}

onMounted(() => {
  loadItems()
})
</script>

<style scoped>
.audit-items-view {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 8px 0;
}

.page-subtitle {
  font-size: 14px;
  color: #666;
  margin: 0;
}

.filter-toolbar {
  background: #fff;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-label {
  font-size: 14px;
  color: #666;
  white-space: nowrap;
}

.filter-select,
.filter-input {
  padding: 6px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background: #fff;
}

.filter-input {
  width: 120px;
}

.date-separator {
  color: #666;
  font-size: 14px;
}

.search-btn,
.reset-btn {
  padding: 6px 16px;
  border: 1px solid #007bff;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.search-btn {
  background: #007bff;
  color: white;
}

.search-btn:hover {
  background: #0056b3;
}

.reset-btn {
  background: #fff;
  color: #007bff;
}

.reset-btn:hover {
  background: #f8f9fa;
}

.search-icon {
  margin-right: 4px;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  border-left: 4px solid #007bff;
}

.stat-card.approved {
  border-left-color: #38a169;
}

.stat-card.rejected {
  border-left-color: #e53e3e;
}

.stat-card.total {
  border-left-color: #6b46c1;
}

.stat-value {
  font-size: 32px;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #666;
}

.items-container {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  min-height: 400px;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  font-size: 14px;
  color: #666;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #999;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-text {
  font-size: 16px;
}

.items-list {
  display: grid;
  gap: 16px;
}

.item-card {
  display: flex;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 16px;
  transition: all 0.3s ease;
}

.item-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.item-card.pending {
  border-left: 4px solid #f6ad55;
}

.item-card.approved {
  border-left: 4px solid #38a169;
}

.item-card.rejected {
  border-left: 4px solid #e53e3e;
}

.item-image {
  width: 120px;
  height: 120px;
  border-radius: 6px;
  overflow: hidden;
  margin-right: 16px;
  flex-shrink: 0;
}

.item-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.no-image {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #f5f5f5;
  color: #999;
}

.no-image-icon {
  font-size: 24px;
  margin-bottom: 4px;
}

.no-image-text {
  font-size: 12px;
}

.item-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.item-name {
  font-size: 18px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0;
}

.item-status {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-pending {
  background: #fffaf0;
  color: #dd6b20;
}

.status-approved {
  background: #f0fff4;
  color: #38a169;
}

.status-rejected {
  background: #fff5f5;
  color: #e53e3e;
}

.item-details {
  flex: 1;
  margin-bottom: 12px;
}

.detail-item {
  display: flex;
  margin-bottom: 6px;
  font-size: 14px;
}

.detail-label {
  color: #666;
  min-width: 60px;
}

.detail-value {
  color: #333;
  flex: 1;
}

.feature-text {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.reward {
  color: #e53e3e;
  font-weight: 500;
}

.item-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  padding: 6px 12px;
  border: 1px solid;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 4px;
}

.approve-btn {
  background: #f0fff4;
  border-color: #38a169;
  color: #38a169;
}

.approve-btn:hover {
  background: #38a169;
  color: white;
}

.reject-btn {
  background: #fff5f5;
  border-color: #e53e3e;
  color: #e53e3e;
}

.reject-btn:hover {
  background: #e53e3e;
  color: white;
}

.detail-btn {
  background: #f8f9fa;
  border-color: #6c757d;
  color: #6c757d;
}

.detail-btn:hover {
  background: #6c757d;
  color: white;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

.page-btn {
  padding: 8px 16px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: #fff;
  color: #333;
  cursor: pointer;
  transition: all 0.3s ease;
}

.page-btn:hover:not(:disabled) {
  background: #007bff;
  color: white;
  border-color: #007bff;
}

.page-btn:disabled {
  background: #f8f9fa;
  color: #999;
  cursor: not-allowed;
}

.page-info {
  font-size: 14px;
  color: #666;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .audit-items-view {
    padding: 16px;
  }
  
  .filter-toolbar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-group {
    justify-content: space-between;
  }
  
  .item-card {
    flex-direction: column;
  }
  
  .item-image {
    width: 100%;
    height: 200px;
    margin-right: 0;
    margin-bottom: 12px;
  }
  
  .item-actions {
    justify-content: center;
  }
}
</style>