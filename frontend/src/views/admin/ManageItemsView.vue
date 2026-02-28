<template>
  <div class="manage-items-view">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1 class="page-title">管理物品状态</h1>
      <p class="page-subtitle">维护已发布信息的状态，处理长期无人认领物品</p>
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
          <option value="2">已通过</option>
          <option value="3">已匹配</option>
          <option value="4">已认领</option>
          <option value="6">已归档</option>
          <option value="7">已无效</option>
        </select>
      </div>
      
      <div class="filter-group">
        <label class="filter-label">长期未认领：</label>
        <select v-model="filterParams.longTerm" class="filter-select">
          <option value="">全部</option>
          <option value="30">超过30天</option>
          <option value="60">超过60天</option>
          <option value="90">超过90天</option>
        </select>
      </div>
      
      <button class="search-btn" @click="loadItems">
        <span class="search-icon">🔍</span>
        搜索
      </button>
      
      <button class="reset-btn" @click="resetFilters">重置</button>
      
      <!-- 批量操作 -->
      <div class="batch-actions">
        <button 
          v-if="selectedItems.length > 0"
          class="batch-btn archive-btn"
          @click="openBatchArchiveDialog"
        >
          <span class="btn-icon">📁</span>
          批量归档 ({{ selectedItems.length }})
        </button>
        
        <button 
          v-if="selectedItems.length > 0"
          class="batch-btn invalid-btn"
          @click="openBatchInvalidDialog"
        >
          <span class="btn-icon">❌</span>
          批量标记无效 ({{ selectedItems.length }})
        </button>
      </div>
    </div>

    <!-- 数据统计 -->
    <div class="stats-cards">
      <div class="stat-card">
        <div class="stat-value">{{ stats.approvedCount }}</div>
        <div class="stat-label">已通过</div>
      </div>
      <div class="stat-card matched">
        <div class="stat-value">{{ stats.matchedCount }}</div>
        <div class="stat-label">已匹配</div>
      </div>
      <div class="stat-card claimed">
        <div class="stat-value">{{ stats.claimedCount }}</div>
        <div class="stat-label">已认领</div>
      </div>
      <div class="stat-card archived">
        <div class="stat-value">{{ stats.archivedCount }}</div>
        <div class="stat-label">已归档</div>
      </div>
      <div class="stat-card long-term">
        <div class="stat-value">{{ stats.longTermCount }}</div>
        <div class="stat-label">长期未认领</div>
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
        <div class="empty-text">暂无物品信息</div>
      </div>
      
      <div v-else class="items-list">
        <div 
          v-for="item in items" 
          :key="item.id"
          class="item-card"
          :class="getStatusClass(item.currentStatus)"
        >
          <!-- 选择框 -->
          <div class="item-select">
            <input 
              type="checkbox" 
              v-model="selectedItems" 
              :value="item.id"
              class="select-checkbox"
            >
          </div>
          
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
            </div>
          </div>
          
          <!-- 物品信息 -->
          <div class="item-info">
            <div class="item-header">
              <h3 class="item-name">{{ item.name }}</h3>
              <div class="item-meta">
                <span class="item-status" :class="getStatusClass(item.currentStatus)">
                  {{ getStatusText(item.currentStatus) }}
                </span>
                <span class="item-time">{{ formatTime(item.createTime) }}</span>
              </div>
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
                <span class="detail-label">特征：</span>
                <span class="detail-value feature-text">{{ item.feature }}</span>
              </div>
              
              <div v-if="item.daysSinceCreate > 30" class="detail-item warning">
                <span class="detail-label">发布时长：</span>
                <span class="detail-value">{{ item.daysSinceCreate }} 天</span>
              </div>
            </div>
            
            <!-- 操作按钮 -->
            <div class="item-actions">
              <button 
                v-if="item.currentStatus === 2"
                class="action-btn match-btn"
                @click="updateItemStatus(item, 3)"
              >
                <span class="btn-icon">🔗</span>
                标记为已匹配
              </button>
              
              <button 
                v-if="item.currentStatus === 3"
                class="action-btn claim-btn"
                @click="updateItemStatus(item, 4)"
              >
                <span class="btn-icon">✅</span>
                标记为已认领
              </button>
              
              <button 
                v-if="item.currentStatus === 2 && item.daysSinceCreate > 30"
                class="action-btn archive-btn"
                @click="openArchiveDialog(item)"
              >
                <span class="btn-icon">📁</span>
                归档
              </button>
              
              <button 
                class="action-btn invalid-btn"
                @click="openInvalidDialog(item)"
              >
                <span class="btn-icon">❌</span>
                标记无效
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

    <!-- 归档弹窗 -->
    <ArchiveDialog 
      v-if="showArchiveDialog"
      :item="currentItem"
      :batch-mode="batchMode"
      :selected-items="selectedItems"
      @confirm="handleArchiveConfirm"
      @cancel="closeArchiveDialog"
    />
    
    <!-- 标记无效弹窗 -->
    <InvalidDialog 
      v-if="showInvalidDialog"
      :item="currentItem"
      :batch-mode="batchMode"
      :selected-items="selectedItems"
      @confirm="handleInvalidConfirm"
      @cancel="closeInvalidDialog"
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
import ArchiveDialog from './components/ArchiveDialog.vue'
import InvalidDialog from './components/InvalidDialog.vue'
import ItemDetailDialog from './components/ItemDetailDialog.vue'

// 筛选参数
const filterParams = reactive({
  itemCategory: '',
  status: '',
  longTerm: ''
})

// 分页参数
const currentPage = ref(1)
const pageSize = 10
const totalPages = ref(1)

// 数据
const items = ref<any[]>([])
const selectedItems = ref<number[]>([])
const loading = ref(false)

// 统计信息
const stats = reactive({
  approvedCount: 0,
  matchedCount: 0,
  claimedCount: 0,
  archivedCount: 0,
  longTermCount: 0
})

// 弹窗控制
const showArchiveDialog = ref(false)
const showInvalidDialog = ref(false)
const showDetailDialog = ref(false)
const currentItem = ref<any>(null)
const batchMode = ref(false)

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
      items.value = (response.data.list || []).map((item: any) => ({
        ...item,
        daysSinceCreate: Math.floor((new Date().getTime() - new Date(item.createTime).getTime()) / (1000 * 60 * 60 * 24))
      }))
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
  stats.approvedCount = items.value.filter(item => item.currentStatus === 2).length
  stats.matchedCount = items.value.filter(item => item.currentStatus === 3).length
  stats.claimedCount = items.value.filter(item => item.currentStatus === 4).length
  stats.archivedCount = items.value.filter(item => item.currentStatus === 6).length
  stats.longTermCount = items.value.filter(item => item.daysSinceCreate > 30).length
}

// 重置筛选
const resetFilters = () => {
  filterParams.itemCategory = ''
  filterParams.status = ''
  filterParams.longTerm = ''
  currentPage.value = 1
  selectedItems.value = []
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
    2: '已通过',
    3: '已匹配',
    4: '已认领',
    6: '已归档',
    7: '已无效'
  }
  return statusMap[status] || '未知状态'
}

// 获取状态样式类
const getStatusClass = (status: number) => {
  const classMap: Record<number, string> = {
    2: 'status-approved',
    3: 'status-matched',
    4: 'status-claimed',
    6: 'status-archived',
    7: 'status-invalid'
  }
  return classMap[status] || ''
}

// 格式化时间
const formatTime = (time: string) => {
  return new Date(time).toLocaleDateString('zh-CN')
}

// 图片加载失败处理
const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  img.style.display = 'none'
  img.parentElement?.querySelector('.no-image')?.classList.remove('hidden')
}

// 更新物品状态
const updateItemStatus = async (item: any, newStatus: number) => {
  try {
    const response = await request.post(`/item/${item.id}/status`, {
      status: newStatus,
      remark: `管理员手动更新状态为${getStatusText(newStatus)}`
    })
    
    if (response.code === 200) {
      // 重新加载列表
      loadItems()
    }
  } catch (error) {
    console.error('更新状态失败:', error)
  }
}

// 打开归档弹窗
const openArchiveDialog = (item: any) => {
  currentItem.value = item
  batchMode.value = false
  showArchiveDialog.value = true
}

// 打开批量归档弹窗
const openBatchArchiveDialog = () => {
  batchMode.value = true
  showArchiveDialog.value = true
}

// 关闭归档弹窗
const closeArchiveDialog = () => {
  showArchiveDialog.value = false
  currentItem.value = null
  batchMode.value = false
}

// 处理归档确认
const handleArchiveConfirm = async (data: any) => {
  try {
    if (batchMode.value) {
      // 批量归档
      const response = await request.post('/item/batch/archive', {
        itemIds: selectedItems.value,
        archiveDesc: data.archiveDesc,
        archiveType: data.archiveType
      })
      
      if (response.code === 200) {
        selectedItems.value = []
        loadItems()
      }
    } else {
      // 单个归档
      const response = await request.post(`/item/${data.itemId}/archive`, {
        archiveDesc: data.archiveDesc
      })
      
      if (response.code === 200) {
        loadItems()
      }
    }
  } catch (error) {
    console.error('归档操作失败:', error)
  }
}

// 打开标记无效弹窗
const openInvalidDialog = (item: any) => {
  currentItem.value = item
  batchMode.value = false
  showInvalidDialog.value = true
}

// 打开批量标记无效弹窗
const openBatchInvalidDialog = () => {
  batchMode.value = true
  showInvalidDialog.value = true
}

// 关闭标记无效弹窗
const closeInvalidDialog = () => {
  showInvalidDialog.value = false
  currentItem.value = null
  batchMode.value = false
}

// 处理标记无效确认
const handleInvalidConfirm = async (data: any) => {
  try {
    if (batchMode.value) {
      // 批量标记无效
      for (const itemId of selectedItems.value) {
        await request.post(`/item/${itemId}/status`, {
          status: 7,
          remark: data.invalidReason
        })
      }
      selectedItems.value = []
    } else {
      // 单个标记无效
      await request.post(`/item/${data.itemId}/status`, {
        status: 7,
        remark: data.invalidReason
      })
    }
    
    loadItems()
  } catch (error) {
    console.error('标记无效失败:', error)
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
.manage-items-view {
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

.filter-select {
  padding: 6px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background: #fff;
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

.batch-actions {
  display: flex;
  gap: 8px;
  margin-left: auto;
}

.batch-btn {
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

.batch-btn.archive-btn {
  background: #fffaf0;
  border-color: #dd6b20;
  color: #dd6b20;
}

.batch-btn.archive-btn:hover {
  background: #dd6b20;
  color: white;
}

.batch-btn.invalid-btn {
  background: #fff5f5;
  border-color: #e53e3e;
  color: #e53e3e;
}

.batch-btn.invalid-btn:hover {
  background: #e53e3e;
  color: white;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
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

.stat-card.matched {
  border-left-color: #3182ce;
}

.stat-card.claimed {
  border-left-color: #38a169;
}

.stat-card.archived {
  border-left-color: #dd6b20;
}

.stat-card.long-term {
  border-left-color: #e53e3e;
}

.stat-value {
  font-size: 28px;
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

.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #999;
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

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
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
  align-items: flex-start;
}

.item-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.item-select {
  margin-right: 12px;
  padding-top: 4px;
}

.select-checkbox {
  width: 16px;
  height: 16px;
}

.item-image {
  width: 100px;
  height: 100px;
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
  align-items: center;
  justify-content: center;
  background: #f5f5f5;
  color: #999;
  font-size: 24px;
}

.item-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.item-name {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0;
  flex: 1;
}

.item-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
}

.item-status {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-approved {
  background: #f0fff4;
  color: #38a169;
}

.status-matched {
  background: #ebf8ff;
  color: #3182ce;
}

.status-claimed {
  background: #f0fff4;
  color: #38a169;
}

.status-archived {
  background: #fffaf0;
  color: #dd6b20;
}

.status-invalid {
  background: #fff5f5;
  color: #e53e3e;
}

.item-time {
  font-size: 12px;
  color: #999;
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

.detail-item.warning {
  color: #e53e3e;
  font-weight: 500;
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

.item-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
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

.match-btn {
  background: #ebf8ff;
  border-color: #3182ce;
  color: #3182ce;
}

.match-btn:hover {
  background: #3182ce;
  color: white;
}

.claim-btn {
  background: #f0fff4;
  border-color: #38a169;
  color: #38a169;
}

.claim-btn:hover {
  background: #38a169;
  color: white;
}

.archive-btn {
  background: #fffaf0;
  border-color: #dd6b20;
  color: #dd6b20;
}

.archive-btn:hover {
  background: #dd6b20;
  color: white;
}

.invalid-btn {
  background: #fff5f5;
  border-color: #e53e3e;
  color: #e53e3e;
}

.invalid-btn:hover {
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

/* 响应式设计 */
@media (max-width: 768px) {
  .manage-items-view {
    padding: 16px;
  }
  
  .filter-toolbar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .batch-actions {
    margin-left: 0;
    justify-content: center;
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