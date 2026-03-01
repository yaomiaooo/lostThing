<!-- src/views/item-admin/pages/PendingReviewView.vue -->
<template>
  <div class="pending-review-page">
    <!-- 纯色背景 -->
    <div class="background-container">
      <div class="solid-background"></div>
    </div>

    <!-- 整体布局 -->
    <div class="layout-container">
      <!-- 左侧导航栏 -->
      <AdminNavigation 
        subtitle="请审核信息"
        active-nav="待审核"
        @logout="handleLogout"
      />

      <!-- 右侧主内容区域 -->
      <main class="main-content">
        <!-- 页面标题 -->
        <section class="page-header">
          <h1 class="page-title">📋 待审核信息</h1>
          <p class="page-subtitle">审核失物/招领信息的真实性、完整性和照片清晰度</p>
        </section>

        <!-- 统计卡片 -->
        <section class="stats-section">
          <div class="stats-grid">
            <div class="stat-card">
              <div class="stat-icon">📥</div>
              <div class="stat-value">{{ stats.pending }}</div>
              <div class="stat-label">待审核</div>
            </div>
            <div class="stat-card">
              <div class="stat-icon">✅</div>
              <div class="stat-value">{{ stats.todayApproved }}</div>
              <div class="stat-label">今日通过</div>
            </div>
            <div class="stat-card">
              <div class="stat-icon">❌</div>
              <div class="stat-value">{{ stats.todayRejected }}</div>
              <div class="stat-label">今日驳回</div>
            </div>
            <div class="stat-card">
              <div class="stat-icon">⏱️</div>
              <div class="stat-value">{{ stats.avgReviewTime }}分钟</div>
              <div class="stat-label">平均审核时长</div>
            </div>
          </div>
        </section>

        <!-- 筛选工具栏 -->
        <section class="toolbar-section">
          <div class="filter-group">
            <select v-model="filterParams.itemCategory" class="filter-select" @change="loadPendingList">
              <option value="">全部类型</option>
              <option value="1">失物</option>
              <option value="2">招领</option>
            </select>
            <select v-model="filterParams.sortOrder" class="filter-select" @change="loadPendingList">
              <option value="asc">最早发布优先</option>
              <option value="desc">最新发布优先</option>
            </select>
          </div>
          <div class="refresh-btn" @click="refreshList">
            <span class="refresh-icon" :class="{ rotating: refreshing }">🔄</span>
            <span>刷新</span>
          </div>
        </section>

        <!-- 待审核列表 -->
        <section class="list-section">
          <!-- 加载状态 -->
          <div v-if="loading" class="loading-container">
            <div class="loading-spinner"></div>
            <div class="loading-text">加载中...</div>
          </div>

          <!-- 空状态 -->
          <div v-else-if="pendingList.length === 0" class="empty-container">
            <div class="empty-icon">🎉</div>
            <div class="empty-title">太棒了！暂无待审核信息</div>
            <div class="empty-desc">所有信息已审核完毕，您可以休息一下</div>
            <button class="history-btn" @click="goToHistory">查看历史记录</button>
          </div>

          <!-- 数据表格 -->
          <div v-else class="table-container">
            <table class="data-table">
              <thead>
                <tr>
                  <th class="col-id">ID</th>
                  <th class="col-type">类型</th>
                  <th class="col-image">图片</th>
                  <th class="col-info">物品信息</th>
                  <th class="col-location">地点</th>
                  <th class="col-time">发布时间</th>
                  <th class="col-publisher">发布人</th>
                  <th class="col-actions">操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in pendingList" :key="item.itemId" class="table-row">
                  <td class="col-id">#{{ item.itemId }}</td>
                  <td class="col-type">
                    <span class="type-tag" :class="item.itemCategory === 1 ? 'lost-tag' : 'found-tag'">
                      {{ item.itemCategory === 1 ? '失物' : '招领' }}
                    </span>
                  </td>
                  <td class="col-image">
                    <div class="image-preview" @click="previewImage(item.firstImageUrl)">
                      <img v-if="item.firstImageUrl" :src="item.firstImageUrl" class="thumb-image" />
                      <div v-else class="no-image">无图</div>
                    </div>
                  </td>
                  <td class="col-info">
                    <div class="info-name">{{ item.name }}</div>
                    <div class="info-type">{{ item.itemTypeName }}</div>
                    <div v-if="item.rewardAmount > 0" class="info-reward">
                      💰 悬赏 ¥{{ item.rewardAmount }}
                    </div>
                  </td>
                  <td class="col-location">
                    <div class="location-campus">{{ item.locationName }}</div>
                    <div v-if="item.locationDetail" class="location-detail">{{ item.locationDetail }}</div>
                  </td>
                  <td class="col-time">
                    <div class="time-main">{{ formatDate(item.createTime) }}</div>
                    <div class="time-ago">{{ timeAgo(item.createTime) }}</div>
                  </td>
                  <td class="col-publisher">
                    <div class="publisher-name">{{ item.contactName }}</div>
                    <div class="publisher-phone">{{ maskPhone(item.contactPhone) }}</div>
                  </td>
                  <td class="col-actions">
                    <div class="action-btns">
                      <button class="action-btn view-btn" @click="viewDetail(item)">
                        查看
                      </button>
                      <button class="action-btn approve-btn" @click="openApproveModal(item)">
                        通过
                      </button>
                      <button class="action-btn reject-btn" @click="openRejectModal(item)">
                        驳回
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>

            <!-- 分页 -->
            <div class="pagination">
              <button 
                class="page-btn" 
                :disabled="pagination.page === 1"
                @click="changePage(pagination.page - 1)"
              >
                上一页
              </button>
              <span class="page-info">
                第 {{ pagination.page }} 页 / 共 {{ pagination.totalPages }} 页
              </span>
              <button 
                class="page-btn" 
                :disabled="pagination.page >= pagination.totalPages"
                @click="changePage(pagination.page + 1)"
              >
                下一页
              </button>
            </div>
          </div>
        </section>
      </main>
    </div>

    <!-- 详情弹窗 -->
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
                <img :src="currentItemImages[currentImageIndex]" class="main-image" />
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
              <div class="info-row">
                <span class="info-label">发生时间：</span>
                <span class="info-value">{{ currentItem.happenTime }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">地点：</span>
                <span class="info-value">{{ currentItem.locationName }} {{ currentItem.locationDetail }}</span>
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
              <div class="info-row">
                <span class="info-label">发布时间：</span>
                <span class="info-value">{{ currentItem.createTime }}</span>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="modal-btn approve-btn" @click="approveItem(currentItem)">通过</button>
          <button class="modal-btn reject-btn" @click="openRejectFromDetail">驳回</button>
          <button class="modal-btn cancel-btn" @click="closeDetailModal">关闭</button>
        </div>
      </div>
    </div>

    <!-- 通过确认弹窗 -->
    <div v-if="showApproveModal" class="modal-overlay" @click.self="closeApproveModal">
      <div class="confirm-modal">
        <div class="modal-header">
          <h3 class="modal-title">确认通过</h3>
          <button class="modal-close" @click="closeApproveModal">×</button>
        </div>
        <div class="modal-body">
          <div class="confirm-content">
            <div class="confirm-icon">✅</div>
            <p class="confirm-text">确定要通过「{{ approvingItem?.name }}」这条信息吗？</p>
            <p class="confirm-hint">通过后将在首页公开展示</p>
          </div>
        </div>
        <div class="modal-footer">
          <button class="modal-btn cancel-btn" @click="closeApproveModal">取消</button>
          <button class="modal-btn approve-btn" :disabled="submitting" @click="confirmApprove">
            <span v-if="submitting" class="loading-spinner-small"></span>
            <span v-else>确认通过</span>
          </button>
        </div>
      </div>
    </div>

    <!-- 驳回弹窗 -->
    <div v-if="showRejectModal" class="modal-overlay" @click.self="closeRejectModal">
      <div class="reject-modal">
        <div class="modal-header">
          <h3 class="modal-title">驳回信息</h3>
          <button class="modal-close" @click="closeRejectModal">×</button>
        </div>
        <div class="modal-body">
          <div class="reject-content">
            <p class="reject-item-name">「{{ rejectingItem?.name }}」</p>
            <div class="form-group">
              <label class="form-label">驳回原因 <span class="required">*</span></label>
              <textarea 
                v-model="rejectReason" 
                class="form-textarea"
                placeholder="请详细说明驳回原因，如：信息不完整、照片不清晰、疑似虚假信息等..."
                rows="4"
              ></textarea>
              <div class="reason-options">
                <button 
                  v-for="reason in commonRejectReasons" 
                  :key="reason"
                  class="reason-tag"
                  @click="selectReason(reason)"
                >
                  {{ reason }}
                </button>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="modal-btn cancel-btn" @click="closeRejectModal">取消</button>
          <button 
            class="modal-btn reject-btn" 
            :disabled="submitting || !rejectReason.trim()"
            @click="confirmReject"
          >
            <span v-if="submitting" class="loading-spinner-small"></span>
            <span v-else>确认驳回</span>
          </button>
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
const refreshing = ref(false)
const pendingList = ref<any[]>([])

/* ================= 筛选参数 ================= */
const filterParams = reactive({
  itemCategory: '',
  sortOrder: 'asc' // 默认最早发布的优先审核
})

/* ================= 分页信息 ================= */
const pagination = reactive({
  page: 1,
  size: 10,
  total: 0,
  totalPages: 1
})

/* ================= 统计信息 ================= */
const stats = reactive({
  pending: 0,
  todayApproved: 0,
  todayRejected: 0,
  avgReviewTime: 0
})

/* ================= 弹窗状态 ================= */
const showDetailModal = ref(false)
const showApproveModal = ref(false)
const showRejectModal = ref(false)
const currentItem = ref<any>(null)
const currentItemImages = ref<string[]>([])
const currentImageIndex = ref(0)
const approvingItem = ref<any>(null)
const rejectingItem = ref<any>(null)
const rejectReason = ref('')
const submitting = ref(false)
const previewImageUrl = ref('')

/* ================= 常用驳回原因 ================= */
const commonRejectReasons = [
  '信息不完整，缺少关键描述',
  '照片不清晰，无法辨认物品',
  '联系方式无效',
  '疑似虚假信息',
  '物品描述与实际不符',
  '重复发布'
]

/* ================= 加载待审核列表 ================= */
const loadPendingList = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/item/admin/list', {
      params: {
        status: '1', // 待审核
        itemCategory: filterParams.itemCategory || undefined,
        page: pagination.page,
        size: pagination.size,
        sortField: 'createTime',
        sortOrder: filterParams.sortOrder
      }
    })
    
    if (res.data.code === 200) {
      pendingList.value = res.data.data.list || []
      pagination.total = res.data.data.total || 0
      pagination.totalPages = Math.ceil(pagination.total / pagination.size)
      
      // 更新统计
      if (res.data.data.statistics) {
        stats.pending = res.data.data.statistics['待审核'] || 0
      }
    }
  } catch (error) {
    console.error('加载待审核列表失败:', error)
    // 模拟数据
    pendingList.value = [
      {
        itemId: 1,
        name: '黑色蓝牙耳机',
        itemCategory: 1,
        itemTypeName: '耳机',
        locationId: 20105,
        locationName: '健行楼',
        locationDetail: 'A108教室',
        happenTime: '2026-02-28 14:30:00',
        feature: '右耳有划痕，品牌为AirPods Pro',
        rewardAmount: 50,
        rewardDesc: '找到必谢',
        contactName: '张三',
        contactPhone: '13800138000',
        createTime: '2026-02-28 15:00:00',
        firstImageUrl: null
      },
      {
        itemId: 2,
        name: '校园卡（李四）',
        itemCategory: 2,
        itemTypeName: '校园卡',
        locationId: 10201,
        locationName: '图书馆',
        locationDetail: '一楼自习区',
        happenTime: '2026-02-28 10:00:00',
        feature: '学号2023123456，姓名李四',
        rewardAmount: 0,
        contactName: '王五',
        contactPhone: '13900139000',
        createTime: '2026-02-28 10:30:00',
        firstImageUrl: null
      }
    ]
    pagination.total = 2
    pagination.totalPages = 1
    stats.pending = 2
  } finally {
    loading.value = false
  }
}

/* ================= 加载今日统计 ================= */
const loadTodayStats = async () => {
  try {
    const today = new Date().toISOString().split('T')[0]
    const res = await axios.get('/api/item/audit/history', {
      params: {
        startDate: today,
        endDate: today,
        page: 1,
        size: 1
      }
    })
    
    if (res.data.code === 200) {
      // 从审核历史计算今日统计
      const list = res.data.data.list || []
      stats.todayApproved = list.filter((item: any) => item.status === 2).length
      stats.todayRejected = list.filter((item: any) => item.status === 5).length
    }
  } catch (error) {
    console.error('加载今日统计失败:', error)
    stats.todayApproved = 5
    stats.todayRejected = 2
    stats.avgReviewTime = 8
  }
}

/* ================= 刷新列表 ================= */
const refreshList = async () => {
  refreshing.value = true
  await loadPendingList()
  await loadTodayStats()
  setTimeout(() => {
    refreshing.value = false
  }, 500)
}

/* ================= 分页切换 ================= */
const changePage = (page: number) => {
  if (page < 1 || page > pagination.totalPages) return
  pagination.page = page
  loadPendingList()
}

/* ================= 查看详情 ================= */
const viewDetail = async (item: any) => {
  currentItem.value = item
  currentImageIndex.value = 0
  
  // 加载物品详情获取图片
  try {
    const res = await axios.get('/api/item/detail', {
      params: { itemId: item.itemId }
    })
    
    if (res.data.code === 200) {
      const detail = res.data.data
      currentItem.value = { ...item, ...detail.item }
      
      // 处理图片
      if (detail.images && detail.images.length > 0) {
        currentItemImages.value = detail.images.map((img: any) => img.url)
      } else if (item.firstImageUrl) {
        currentItemImages.value = [item.firstImageUrl]
      } else {
        currentItemImages.value = []
      }
    }
  } catch (error) {
    console.error('加载详情失败:', error)
    currentItemImages.value = item.firstImageUrl ? [item.firstImageUrl] : []
  }
  
  showDetailModal.value = true
}

const closeDetailModal = () => {
  showDetailModal.value = false
  currentItem.value = null
  currentItemImages.value = []
}

/* ================= 通过审核 ================= */
const openApproveModal = (item: any) => {
  approvingItem.value = item
  showApproveModal.value = true
}

const closeApproveModal = () => {
  showApproveModal.value = false
  approvingItem.value = null
}

const confirmApprove = async () => {
  if (!approvingItem.value) return
  
  submitting.value = true
  try {
    const res = await axios.post('/api/item/audit', {
      itemId: approvingItem.value.itemId,
      status: 2 // 通过
    })
    
    if (res.data.code === 200) {
      // 从列表中移除
      pendingList.value = pendingList.value.filter(
        item => item.itemId !== approvingItem.value.itemId
      )
      stats.pending--
      stats.todayApproved++
      closeApproveModal()
    }
  } catch (error) {
    console.error('审核通过失败:', error)
    alert('操作失败，请重试')
  } finally {
    submitting.value = false
  }
}

/* ================= 驳回审核 ================= */
const openRejectModal = (item: any) => {
  rejectingItem.value = item
  rejectReason.value = ''
  showRejectModal.value = true
}

const openRejectFromDetail = () => {
  rejectingItem.value = currentItem.value
  rejectReason.value = ''
  showDetailModal.value = false
  showRejectModal.value = true
}

const closeRejectModal = () => {
  showRejectModal.value = false
  rejectingItem.value = null
  rejectReason.value = ''
}

const selectReason = (reason: string) => {
  rejectReason.value = reason
}

const confirmReject = async () => {
  if (!rejectingItem.value || !rejectReason.value.trim()) return
  
  submitting.value = true
  try {
    const res = await axios.post('/api/item/audit', {
      itemId: rejectingItem.value.itemId,
      status: 5, // 驳回
      rejectReason: rejectReason.value.trim()
    })
    
    if (res.data.code === 200) {
      // 从列表中移除
      pendingList.value = pendingList.value.filter(
        item => item.itemId !== rejectingItem.value.itemId
      )
      stats.pending--
      stats.todayRejected++
      closeRejectModal()
    }
  } catch (error) {
    console.error('驳回失败:', error)
    alert('操作失败，请重试')
  } finally {
    submitting.value = false
  }
}

/* ================= 图片预览 ================= */
const previewImage = (url: string | null) => {
  if (!url) return
  previewImageUrl.value = url
}

const closeImagePreview = () => {
  previewImageUrl.value = ''
}

/* ================= 工具函数 ================= */
const formatDate = (timeStr: string) => {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  return `${date.getMonth() + 1}/${date.getDate()} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
}

const timeAgo = (timeStr: string) => {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  const now = new Date()
  const diff = Math.floor((now.getTime() - date.getTime()) / 1000)
  
  if (diff < 60) return '刚刚'
  if (diff < 3600) return `${Math.floor(diff / 60)}分钟前`
  if (diff < 86400) return `${Math.floor(diff / 3600)}小时前`
  return `${Math.floor(diff / 86400)}天前`
}

const maskPhone = (phone: string) => {
  if (!phone || phone.length !== 11) return phone
  return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2')
}

/* ================= 路由跳转 ================= */
const handleLogout = () => {
  router.push('/login')
}

const goToHistory = () => {
  router.push('/item-admin/history')
}

/* ================= 生命周期 ================= */
onMounted(() => {
  loadPendingList()
  loadTodayStats()
})
</script>

<style scoped>
/* 基础布局 */
.pending-review-page {
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

.stat-icon {
  font-size: 32px;
  margin-bottom: 10px;
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
  font-size: 14px;
  color: rgba(166, 124, 82, 0.7);
}

/* 工具栏 */
.toolbar-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(15px);
  border-radius: 12px;
  padding: 15px 20px;
  border: 2px solid rgba(166, 124, 82, 0.2);
}

.filter-group {
  display: flex;
  gap: 12px;
}

.filter-select {
  padding: 10px 15px;
  border: 1.6px solid rgba(166, 124, 82, 0.4);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.4);
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
  cursor: pointer;
  outline: none;
}

.filter-select:focus {
  border-color: rgba(243, 129, 129, 0.7);
}

.refresh-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: linear-gradient(to right, #f38181, #f77d5f);
  color: white;
  border-radius: 10px;
  cursor: pointer;
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  transition: all 0.3s ease;
}

.refresh-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(243, 129, 129, 0.3);
}

.refresh-icon {
  font-size: 16px;
  transition: transform 0.5s ease;
}

.refresh-icon.rotating {
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
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

/* 加载状态 */
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

/* 空状态 */
.empty-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 0;
  text-align: center;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 20px;
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

.history-btn {
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

.history-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(243, 129, 129, 0.4);
}

/* 数据表格 */
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
  vertical-align: top;
}

.table-row:hover {
  background: rgba(255, 255, 255, 0.3);
}

.col-id { width: 60px; }
.col-type { width: 80px; }
.col-image { width: 80px; }
.col-info { min-width: 150px; }
.col-location { min-width: 120px; }
.col-time { width: 100px; }
.col-publisher { width: 120px; }
.col-actions { width: 180px; }

/* 类型标签 */
.type-tag {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  color: white;
}

.lost-tag {
  background: linear-gradient(135deg, #ff9a9e 0%, #fad0c4 100%);
}

.found-tag {
  background: linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%);
}

/* 图片预览 */
.image-preview {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  background: rgba(166, 124, 82, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
}

.thumb-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.no-image {
  font-size: 12px;
  color: rgba(166, 124, 82, 0.5);
}

/* 信息列 */
.info-name {
  font-weight: 600;
  color: #a67c52;
  margin-bottom: 4px;
}

.info-type {
  font-size: 12px;
  color: rgba(166, 124, 82, 0.7);
  margin-bottom: 4px;
}

.info-reward {
  font-size: 12px;
  color: #ff9800;
  font-weight: 600;
}

/* 地点 */
.location-campus {
  font-weight: 500;
  color: #a67c52;
}

.location-detail {
  font-size: 12px;
  color: rgba(166, 124, 82, 0.7);
  margin-top: 4px;
}

/* 时间 */
.time-main {
  font-weight: 500;
  color: #a67c52;
}

.time-ago {
  font-size: 12px;
  color: rgba(166, 124, 82, 0.6);
  margin-top: 4px;
}

/* 发布人 */
.publisher-name {
  font-weight: 500;
  color: #a67c52;
}

.publisher-phone {
  font-size: 12px;
  color: rgba(166, 124, 82, 0.6);
  margin-top: 4px;
}

/* 操作按钮 */
.action-btns {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.action-btn {
  padding: 6px 12px;
  border: none;
  border-radius: 8px;
  font-family: "Comic Sans MS", cursive;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.view-btn {
  background: rgba(166, 124, 82, 0.1);
  color: #a67c52;
  border: 1px solid rgba(166, 124, 82, 0.3);
}

.view-btn:hover {
  background: rgba(166, 124, 82, 0.2);
}

.approve-btn {
  background: linear-gradient(to right, #4caf50, #8bc34a);
  color: white;
}

.approve-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
}

.reject-btn {
  background: linear-gradient(to right, #f38181, #f77d5f);
  color: white;
}

.reject-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(243, 129, 129, 0.3);
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

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: rgba(166, 124, 82, 0.8);
}

/* 模态框通用样式 */
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
  display: flex;
  align-items: center;
  gap: 8px;
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
  opacity: 0.7;
  transition: all 0.3s ease;
}

.thumb.active,
.thumb:hover {
  border-color: #f38181;
  opacity: 1;
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
  font-size: 15px;
  color: #a67c52;
  font-weight: 500;
}

.info-value.description {
  line-height: 1.6;
  background: rgba(166, 124, 82, 0.05);
  padding: 12px;
  border-radius: 8px;
}

.info-value.reward {
  color: #ff9800;
  font-weight: 600;
}

/* 确认弹窗 */
.confirm-modal,
.reject-modal {
  background: white;
  border-radius: 20px;
  width: 90%;
  max-width: 450px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.confirm-content {
  text-align: center;
  padding: 20px;
}

.confirm-icon {
  font-size: 64px;
  margin-bottom: 20px;
}

.confirm-text {
  font-family: "Comic Sans MS", cursive;
  font-size: 18px;
  color: #a67c52;
  margin-bottom: 10px;
}

.confirm-hint {
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: rgba(166, 124, 82, 0.6);
}

/* 驳回弹窗 */
.reject-content {
  padding: 10px;
}

.reject-item-name {
  font-family: "Comic Sans MS", cursive;
  font-size: 16px;
  color: #a67c52;
  font-weight: 600;
  margin-bottom: 20px;
  text-align: center;
}

.form-group {
  margin-bottom: 20px;
}

.form-label {
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
}

.required {
  color: #ff4d4f;
}

.form-textarea {
  width: 100%;
  padding: 12px;
  border: 1.6px solid rgba(166, 124, 82, 0.4);
  border-radius: 10px;
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
  resize: vertical;
  box-sizing: border-box;
  outline: none;
}

.form-textarea:focus {
  border-color: rgba(243, 129, 129, 0.7);
  box-shadow: 0 0 0 3px rgba(243, 129, 129, 0.1);
}

.reason-options {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}

.reason-tag {
  padding: 6px 12px;
  border: 1px solid rgba(166, 124, 82, 0.3);
  border-radius: 15px;
  background: rgba(255, 255, 255, 0.5);
  font-family: "Comic Sans MS", cursive;
  font-size: 12px;
  color: rgba(166, 124, 82, 0.8);
  cursor: pointer;
  transition: all 0.3s ease;
}

.reason-tag:hover {
  border-color: #f38181;
  color: #f38181;
  background: rgba(243, 129, 129, 0.1);
}

/* 加载动画小尺寸 */
.loading-spinner-small {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
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

/* 响应式设计 */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .detail-content {
    flex-direction: column;
  }
  
  .detail-images {
    flex: 1;
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
  
  .stat-card {
    padding: 15px;
  }
  
  .stat-value {
    font-size: 22px;
  }
  
  .toolbar-section {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }
  
  .filter-group {
    justify-content: space-between;
  }
  
  .table-container {
    font-size: 12px;
  }
  
  .data-table th,
  .data-table td {
    padding: 10px 8px;
  }
  
  .col-id,
  .col-publisher {
    display: none;
  }
  
  .action-btns {
    flex-direction: column;
    gap: 4px;
  }
  
  .action-btn {
    padding: 8px;
    font-size: 11px;
  }
  
  .modal-overlay {
    padding: 10px;
  }
  
  .detail-modal {
    width: 100%;
    max-height: 95vh;
  }
}
</style>