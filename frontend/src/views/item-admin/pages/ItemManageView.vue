<!-- src/views/item-admin/pages/ItemManageView.vue -->
<template>
  <div class="item-manage-page">
    <!-- 纯色背景 -->
    <div class="background-container">
      <div class="solid-background"></div>
    </div>

    <!-- 整体布局 -->
    <div class="layout-container">
      <!-- 左侧导航栏 -->
      <AdminNavigation />

      <!-- 右侧主内容区域 -->
      <main class="main-content">
        <!-- 页面标题 -->
        <section class="page-header">
          <h1 class="page-title">📦 物品管理</h1>
          <p class="page-subtitle">管理已发布物品状态，处理认领申请，归档长期无人认领物品</p>
        </section>

        <!-- 统计概览 -->
        <section class="stats-section">
          <div class="stats-grid">
            <div class="stat-card" @click="quickFilter('all')">
              <div class="stat-icon">📦</div>
              <div class="stat-value">{{ overview.total }}</div>
              <div class="stat-label">全部物品</div>
            </div>
            <div class="stat-card highlight" @click="quickFilter('2')">
              <div class="stat-icon">✅</div>
              <div class="stat-value">{{ overview.approved }}</div>
              <div class="stat-label">已通过</div>
            </div>
            <div class="stat-card warning" @click="quickFilter('3')">
              <div class="stat-icon">🤝</div>
              <div class="stat-value">{{ overview.matched }}</div>
              <div class="stat-label">已匹配</div>
            </div>
            <div class="stat-card success" @click="quickFilter('4')">
              <div class="stat-icon">🎉</div>
              <div class="stat-value">{{ overview.claimed }}</div>
              <div class="stat-label">已认领</div>
            </div>
            <div class="stat-card danger" @click="quickFilter('archived')">
              <div class="stat-icon">📁</div>
              <div class="stat-value">{{ overview.archived }}</div>
              <div class="stat-label">已归档</div>
            </div>
            <div class="stat-card info" @click="openUnclaimedModal">
              <div class="stat-icon">⏰</div>
              <div class="stat-value">{{ overview.longTermUnclaimed }}</div>
              <div class="stat-label">超30天未认领</div>
            </div>
          </div>
        </section>

        <!-- 筛选工具栏 -->
        <section class="toolbar-section">
          <div class="filter-row">
            <div class="filter-group">
              <select v-model="filterParams.status" class="filter-select" @change="loadItemList">
                <option value="">全部状态</option>
                <option value="2">已通过</option>
                <option value="3">已匹配</option>
                <option value="4">已认领</option>
                <option value="5">已驳回</option>
                <option value="6">已取消</option>
                <option value="7">已归档</option>
              </select>
              <select v-model="filterParams.itemCategory" class="filter-select" @change="loadItemList">
                <option value="">全部类型</option>
                <option value="1">失物</option>
                <option value="2">招领</option>
              </select>
              <select v-model="filterParams.locationId" class="filter-select" @change="loadItemList">
                <option value="">全部校区</option>
                <option value="1">朝晖校区</option>
                <option value="2">屏峰校区</option>
                <option value="3">莫干山校区</option>
              </select>
            </div>
            <div class="search-box">
              <input 
                v-model="filterParams.keyword" 
                type="text" 
                class="search-input" 
                placeholder="搜索物品名称、地点..."
                @keyup.enter="loadItemList"
              />
              <button class="search-btn" @click="loadItemList">🔍</button>
            </div>
          </div>
          <div class="action-row">
            <div class="batch-actions" v-if="selectedItems.length > 0">
              <span class="selected-count">已选 {{ selectedItems.length }} 项</span>
              <button class="batch-btn archive-btn" @click="batchArchive">
                📁 批量归档
              </button>
              <button class="batch-btn delete-btn" @click="batchDelete">
                🗑️ 批量删除
              </button>
            </div>
            <div class="refresh-btn" @click="refreshList">
              <span class="refresh-icon" :class="{ rotating: refreshing }">🔄</span>
              <span>刷新</span>
            </div>
          </div>
        </section>

        <!-- 物品列表 -->
        <section class="list-section">
          <!-- 加载状态 -->
          <div v-if="loading" class="loading-container">
            <div class="loading-spinner"></div>
            <div class="loading-text">加载中...</div>
          </div>

          <!-- 空状态 -->
          <div v-else-if="itemList.length === 0" class="empty-container">
            <div class="empty-icon">📭</div>
            <div class="empty-title">暂无物品记录</div>
            <div class="empty-desc">当前筛选条件下没有符合条件的物品</div>
          </div>

          <!-- 数据表格 -->
          <div v-else class="table-container">
            <table class="data-table">
              <thead>
                <tr>
                  <th class="col-checkbox">
                    <input 
                      type="checkbox" 
                      :checked="isAllSelected"
                      @change="toggleSelectAll"
                    />
                  </th>
                  <th class="col-id">ID</th>
                  <th class="col-type">类型</th>
                  <th class="col-image">图片</th>
                  <th class="col-info">物品信息</th>
                  <th class="col-status">状态</th>
                  <th class="col-claims">认领申请</th>
                  <th class="col-time">发布时间</th>
                  <th class="col-actions">操作</th>
                </tr>
              </thead>
              <tbody>
                <tr 
                  v-for="item in itemList" 
                  :key="item.itemId"
                  class="table-row"
                  :class="{ 'row-selected': selectedItems.includes(item.itemId) }"
                >
                  <td class="col-checkbox">
                    <input 
                      type="checkbox" 
                      :checked="selectedItems.includes(item.itemId)"
                      @change="toggleSelectItem(item.itemId)"
                    />
                  </td>
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
                    <div class="info-location">📍 {{ item.locationName }}</div>
                    <div v-if="item.rewardAmount > 0" class="info-reward">
                      💰 ¥{{ item.rewardAmount }}
                    </div>
                  </td>
                  <td class="col-status">
                    <span class="status-tag" :class="getStatusClass(item.currentStatus)">
                      {{ item.currentStatusName }}
                    </span>
                    <div v-if="item.archiveDesc" class="archive-desc" :title="item.archiveDesc">
                      📁 {{ truncateText(item.archiveDesc, 15) }}
                    </div>
                  </td>
                  <td class="col-claims">
                    <div v-if="item.pendingClaimCount > 0" class="claim-badge" @click="viewClaims(item)">
                      {{ item.pendingClaimCount }} 条待审核
                    </div>
                    <div v-else-if="item.claimCount > 0" class="claim-info">
                      {{ item.claimCount }} 条申请
                    </div>
                    <div v-else class="claim-empty">-</div>
                  </td>
                  <td class="col-time">
                    <div class="time-main">{{ formatDate(item.createTime) }}</div>
                    <div class="time-ago">{{ timeAgo(item.createTime) }}</div>
                  </td>
                  <td class="col-actions">
                    <div class="action-btns">
                      <button class="action-btn view-btn" @click="viewDetail(item)">查看</button>
                      <button 
                        v-if="item.currentStatus === 2 || item.currentStatus === 3"
                        class="action-btn status-btn"
                        @click="openStatusModal(item)"
                      >
                        更新状态
                      </button>
                      <button 
                        v-if="item.pendingClaimCount > 0"
                        class="action-btn claim-btn"
                        @click="viewClaims(item)"
                      >
                        审核认领
                      </button>
                      <button 
                        v-if="canArchive(item)"
                        class="action-btn archive-btn"
                        @click="openArchiveModal(item)"
                      >
                        归档
                      </button>
                      <button 
                        v-if="item.currentStatus === 5 || item.currentStatus === 6"
                        class="action-btn delete-btn"
                        @click="confirmDelete(item)"
                      >
                        删除
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
                第 {{ pagination.page }} 页 / 共 {{ pagination.totalPages }} 页（共 {{ pagination.total }} 条）
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

    <!-- 物品详情弹窗 -->
    <div v-if="showDetailModal" class="modal-overlay" @click.self="closeDetailModal">
      <div class="detail-modal">
        <div class="modal-header">
          <h3 class="modal-title">物品详情</h3>
          <button class="modal-close" @click="closeDetailModal">×</button>
        </div>
        <div class="modal-body" v-if="currentItem">
          <!-- 详情内容... -->
        </div>
        <div class="modal-footer">
          <button class="modal-btn cancel-btn" @click="closeDetailModal">关闭</button>
        </div>
      </div>
    </div>

    <!-- 状态更新弹窗 -->
    <div v-if="showStatusModal" class="modal-overlay" @click.self="closeStatusModal">
      <div class="status-modal">
        <div class="modal-header">
          <h3 class="modal-title">更新物品状态</h3>
          <button class="modal-close" @click="closeStatusModal">×</button>
        </div>
        <div class="modal-body">
          <div class="current-item">
            <span class="item-name">{{ updatingItem?.name }}</span>
            <span class="current-status">当前：{{ updatingItem?.currentStatusName }}</span>
          </div>
          <div class="status-options">
            <div 
              v-for="status in availableStatuses" 
              :key="status.value"
              class="status-option"
              :class="{ active: newStatus === status.value }"
              @click="newStatus = status.value"
            >
              <div class="status-icon">{{ status.icon }}</div>
              <div class="status-info">
                <div class="status-name">{{ status.label }}</div>
                <div class="status-desc">{{ status.desc }}</div>
              </div>
            </div>
          </div>
          <div class="form-group" v-if="newStatus === 4">
            <label class="form-label">认领人信息</label>
            <input 
              v-model="statusRemark" 
              type="text" 
              class="form-input" 
              placeholder="请输入认领人姓名和联系方式..."
            />
          </div>
          <div class="form-group" v-if="newStatus === 7">
            <label class="form-label">归档说明 <span class="required">*</span></label>
            <textarea 
              v-model="statusRemark" 
              class="form-textarea"
              rows="3"
              placeholder="请说明归档原因，如：超过30天无人认领、移交保卫处等..."
            ></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="modal-btn cancel-btn" @click="closeStatusModal">取消</button>
          <button 
            class="modal-btn confirm-btn" 
            :disabled="!newStatus || (newStatus === 7 && !statusRemark.trim())"
            @click="confirmUpdateStatus"
          >
            确认更新
          </button>
        </div>
      </div>
    </div>

    <!-- 归档弹窗 -->
    <div v-if="showArchiveModal" class="modal-overlay" @click.self="closeArchiveModal">
      <div class="archive-modal">
        <div class="modal-header">
          <h3 class="modal-title">归档物品</h3>
          <button class="modal-close" @click="closeArchiveModal">×</button>
        </div>
        <div class="modal-body">
          <div class="archive-item">
            <span class="item-name">{{ archivingItem?.name }}</span>
          </div>
          <div class="form-group">
            <label class="form-label">归档类型 <span class="required">*</span></label>
            <div class="archive-types">
              <button 
                v-for="type in archiveTypes" 
                :key="type"
                class="type-btn"
                :class="{ active: archiveType === type }"
                @click="archiveType = type"
              >
                {{ type }}
              </button>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">归档说明 <span class="required">*</span></label>
            <textarea 
              v-model="archiveDesc" 
              class="form-textarea"
              rows="3"
              placeholder="请详细说明归档原因和处理方式..."
            ></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="modal-btn cancel-btn" @click="closeArchiveModal">取消</button>
          <button 
            class="modal-btn archive-confirm-btn" 
            :disabled="!archiveType || !archiveDesc.trim()"
            @click="confirmArchive"
          >
            确认归档
          </button>
        </div>
      </div>
    </div>

    <!-- 认领申请列表弹窗 -->
    <div v-if="showClaimsModal" class="modal-overlay" @click.self="closeClaimsModal">
      <div class="claims-modal">
        <div class="modal-header">
          <h3 class="modal-title">认领申请审核</h3>
          <button class="modal-close" @click="closeClaimsModal">×</button>
        </div>
        <div class="modal-body">
          <div class="claims-item-info" v-if="claimsItem">
            <img :src="claimsItem.firstImageUrl || '/home/默认.jpg'" class="claims-item-image" />
            <div class="claims-item-detail">
              <div class="claims-item-name">{{ claimsItem.name }}</div>
              <div class="claims-item-status">当前状态：{{ claimsItem.currentStatusName }}</div>
            </div>
          </div>
          
          <div class="claims-list" v-if="claimsList.length > 0">
            <div 
              v-for="claim in claimsList" 
              :key="claim.claimId"
              class="claim-card"
            >
              <div class="claim-header">
                <div class="claim-user">
                  <div class="user-avatar">{{ claim.claimUserName?.[0] || '?' }}</div>
                  <div class="user-info">
                    <div class="user-name">{{ claim.claimUserName }}</div>
                    <div class="user-phone">{{ maskPhone(claim.claimUserPhone) }}</div>
                  </div>
                </div>
                <div class="claim-status" :class="'status-' + claim.status">
                  {{ claim.statusName }}
                </div>
              </div>
              <div class="claim-content">
                <div class="claim-label">认领说明：</div>
                <div class="claim-proof">{{ claim.proofFeature }}</div>
              </div>
              <div class="claim-time">申请时间：{{ claim.createTime }}</div>
              <div class="claim-actions" v-if="claim.status === 0">
                <button class="claim-btn approve" @click="auditClaim(claim.claimId, 1)">
                  ✓ 通过
                </button>
                <button class="claim-btn reject" @click="auditClaim(claim.claimId, 2)">
                  ✗ 驳回
                </button>
              </div>
            </div>
          </div>
          
          <div v-else class="claims-empty">
            <div class="empty-icon">📭</div>
            <div class="empty-text">暂无认领申请</div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="modal-btn cancel-btn" @click="closeClaimsModal">关闭</button>
        </div>
      </div>
    </div>

    <!-- 长期未认领物品弹窗 -->
    <div v-if="showUnclaimedModal" class="modal-overlay" @click.self="closeUnclaimedModal">
      <div class="unclaimed-modal">
        <div class="modal-header">
          <h3 class="modal-title">长期无人认领物品（超过30天）</h3>
          <button class="modal-close" @click="closeUnclaimedModal">×</button>
        </div>
        <div class="modal-body">
          <div class="unclaimed-list" v-if="unclaimedList.length > 0">
            <div 
              v-for="item in unclaimedList" 
              :key="item.itemId"
              class="unclaimed-item"
            >
              <div class="item-info">
                <div class="item-name">{{ item.name }}</div>
                <div class="item-location">📍 {{ item.locationName }}</div>
                <div class="item-time">发布于 {{ timeAgo(item.createTime) }}</div>
              </div>
              <button class="quick-archive-btn" @click="quickArchive(item)">
                归档
              </button>
            </div>
          </div>
          <div v-else class="unclaimed-empty">
            <div class="empty-icon">🎉</div>
            <div class="empty-text">暂无长期未认领物品</div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="modal-btn cancel-btn" @click="closeUnclaimedModal">关闭</button>
          <button 
            v-if="unclaimedList.length > 0"
            class="modal-btn batch-archive-btn"
            @click="batchArchiveUnclaimed"
          >
            批量归档全部
          </button>
        </div>
      </div>
    </div>

    <!-- 删除确认弹窗 -->
    <div v-if="showDeleteModal" class="modal-overlay" @click.self="closeDeleteModal">
      <div class="confirm-modal">
        <div class="modal-header">
          <h3 class="modal-title">确认删除</h3>
          <button class="modal-close" @click="closeDeleteModal">×</button>
        </div>
        <div class="modal-body">
          <div class="confirm-content">
            <div class="confirm-icon">⚠️</div>
            <p class="confirm-text">确定要删除「{{ deletingItem?.name }}」吗？</p>
            <p class="confirm-hint">删除后不可恢复，请谨慎操作！</p>
          </div>
        </div>
        <div class="modal-footer">
          <button class="modal-btn cancel-btn" @click="closeDeleteModal">取消</button>
          <button class="modal-btn delete-confirm-btn" @click="confirmDeleteItem">
            确认删除
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
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import AdminNavigation from '../components/AdminNavigation.vue'

const router = useRouter()

/* ================= 数据状态 ================= */
const loading = ref(false)
const refreshing = ref(false)
const itemList = ref<any[]>([])

/* ================= 筛选参数 ================= */
const filterParams = reactive({
  status: '',
  itemCategory: '',
  locationId: '',
  keyword: '',
  sortField: 'createTime',
  sortOrder: 'desc'
})

/* ================= 分页信息 ================= */
const pagination = reactive({
  page: 1,
  size: 10,
  total: 0,
  totalPages: 1
})

/* ================= 统计概览 ================= */
const overview = reactive({
  total: 0,
  approved: 0,
  matched: 0,
  claimed: 0,
  archived: 0,
  longTermUnclaimed: 0
})

/* ================= 批量选择 ================= */
const selectedItems = ref<number[]>([])

const isAllSelected = computed(() => {
  return itemList.value.length > 0 && selectedItems.value.length === itemList.value.length
})

/* ================= 弹窗状态 ================= */
const showDetailModal = ref(false)
const showStatusModal = ref(false)
const showArchiveModal = ref(false)
const showClaimsModal = ref(false)
const showUnclaimedModal = ref(false)
const showDeleteModal = ref(false)

const currentItem = ref<any>(null)
const updatingItem = ref<any>(null)
const archivingItem = ref<any>(null)
const claimsItem = ref<any>(null)
const deletingItem = ref<any>(null)

/* ================= 状态更新 ================= */
const newStatus = ref<number | null>(null)
const statusRemark = ref('')

const availableStatuses = [
  { value: 2, label: '已通过', icon: '✅', desc: '信息审核通过，正常展示' },
  { value: 3, label: '已匹配', icon: '🤝', desc: '找到匹配信息，等待认领确认' },
  { value: 4, label: '已认领', icon: '🎉', desc: '物品已被成功认领' },
  { value: 7, label: '已归档', icon: '📁', desc: '长期无人认领或已处理完毕' }
]

/* ================= 归档 ================= */
const archiveType = ref('')
const archiveDesc = ref('')
const archiveTypes = ['移交保卫处', '捐赠处理', '报废处理', '其他']

/* ================= 认领申请 ================= */
const claimsList = ref<any[]>([])
const unclaimedList = ref<any[]>([])

/* ================= 图片预览 ================= */
const previewImageUrl = ref('')

/* ================= 加载物品列表 ================= */
const loadItemList = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/item/admin/list', {
      params: {
        page: pagination.page,
        size: pagination.size,
        status: filterParams.status || undefined,
        itemCategory: filterParams.itemCategory || undefined,
        locationId: filterParams.locationId || undefined,
        keyword: filterParams.keyword || undefined,
        sortField: filterParams.sortField,
        sortOrder: filterParams.sortOrder
      }
    })
    
    if (res.data.code === 200) {
      itemList.value = res.data.data.list || []
      pagination.total = res.data.data.total || 0
      pagination.totalPages = Math.ceil(pagination.total / pagination.size)
      
      // 更新统计
      if (res.data.data.statistics) {
        const s = res.data.data.statistics
        overview.approved = s['已通过'] || 0
        overview.matched = s['已匹配'] || 0
        overview.claimed = s['已认领'] || 0
        overview.archived = s['已归档'] || 0
        overview.total = overview.approved + overview.matched + overview.claimed + 
                         overview.archived + (s['待审核'] || 0) + (s['已驳回'] || 0) + (s['已取消'] || 0)
      }
    }
  } catch (error) {
    console.error('加载物品列表失败:', error)
    // 模拟数据
    itemList.value = [
      {
        itemId: 1,
        name: '黑色蓝牙耳机',
        itemCategory: 1,
        currentStatus: 2,
        currentStatusName: '已通过',
        locationName: '健行楼 A108',
        rewardAmount: 50,
        claimCount: 2,
        pendingClaimCount: 1,
        createTime: '2026-02-28 15:00:00',
        firstImageUrl: null
      },
      {
        itemId: 2,
        name: '校园卡（李四）',
        itemCategory: 2,
        currentStatus: 3,
        currentStatusName: '已匹配',
        locationName: '图书馆一楼',
        rewardAmount: 0,
        claimCount: 1,
        pendingClaimCount: 0,
        createTime: '2026-02-27 10:30:00',
        firstImageUrl: null
      }
    ]
    overview.total = 2
    overview.approved = 1
    overview.matched = 1
  } finally {
    loading.value = false
  }
}

/* ================= 加载长期未认领统计 ================= */
const loadUnclaimedStats = async () => {
  try {
    const res = await axios.get('/api/item/unclaimed/long-term', {
      params: { days: 30, page: 1, size: 1 }
    })
    if (res.data.code === 200) {
      overview.longTermUnclaimed = res.data.data.total || 0
    }
  } catch (error) {
    console.error('加载未认领统计失败:', error)
    overview.longTermUnclaimed = 3
  }
}

/* ================= 刷新列表 ================= */
const refreshList = async () => {
  refreshing.value = true
  selectedItems.value = []
  await loadItemList()
  await loadUnclaimedStats()
  setTimeout(() => {
    refreshing.value = false
  }, 500)
}

/* ================= 分页切换 ================= */
const changePage = (page: number) => {
  if (page < 1 || page > pagination.totalPages) return
  pagination.page = page
  loadItemList()
}

/* ================= 快速筛选 ================= */
const quickFilter = (status: string) => {
  filterParams.status = status === 'all' ? '' : status
  pagination.page = 1
  loadItemList()
}

/* ================= 批量选择 ================= */
const toggleSelectAll = () => {
  if (isAllSelected.value) {
    selectedItems.value = []
  } else {
    selectedItems.value = itemList.value.map(item => item.itemId)
  }
}

const toggleSelectItem = (itemId: number) => {
  const index = selectedItems.value.indexOf(itemId)
  if (index > -1) {
    selectedItems.value.splice(index, 1)
  } else {
    selectedItems.value.push(itemId)
  }
}

/* ================= 查看详情 ================= */
const viewDetail = (item: any) => {
  currentItem.value = item
  showDetailModal.value = true
}

const closeDetailModal = () => {
  showDetailModal.value = false
  currentItem.value = null
}

/* ================= 状态更新 ================= */
const openStatusModal = (item: any) => {
  updatingItem.value = item
  newStatus.value = null
  statusRemark.value = ''
  showStatusModal.value = true
}

const closeStatusModal = () => {
  showStatusModal.value = false
  updatingItem.value = null
  newStatus.value = null
  statusRemark.value = ''
}

const confirmUpdateStatus = async () => {
  if (!updatingItem.value || !newStatus.value) return
  
  try {
    const res = await axios.post(`/api/item/${updatingItem.value.itemId}/status`, {
      status: newStatus.value,
      remark: statusRemark.value
    })
    
    if (res.data.code === 200) {
      await loadItemList()
      closeStatusModal()
    }
  } catch (error) {
    console.error('更新状态失败:', error)
    alert('操作失败，请重试')
  }
}

/* ================= 归档 ================= */
const canArchive = (item: any) => {
  return item.currentStatus === 2 || item.currentStatus === 3 || 
         (item.currentStatus !== 4 && item.currentStatus !== 7)
}

const openArchiveModal = (item: any) => {
  archivingItem.value = item
  archiveType.value = ''
  archiveDesc.value = ''
  showArchiveModal.value = true
}

const closeArchiveModal = () => {
  showArchiveModal.value = false
  archivingItem.value = null
  archiveType.value = ''
  archiveDesc.value = ''
}

const confirmArchive = async () => {
  if (!archivingItem.value || !archiveType.value || !archiveDesc.value.trim()) return
  
  try {
    const res = await axios.post(`/api/item/${archivingItem.value.itemId}/archive`, {
      archiveDesc: `[${archiveType.value}] ${archiveDesc.value}`
    })
    
    if (res.data.code === 200) {
      await loadItemList()
      await loadUnclaimedStats()
      closeArchiveModal()
    }
  } catch (error) {
    console.error('归档失败:', error)
    alert('操作失败，请重试')
  }
}

/* ================= 批量归档 ================= */
const batchArchive = async () => {
  if (selectedItems.value.length === 0) return
  
  const confirm = window.confirm(`确定要批量归档 ${selectedItems.value.length} 个物品吗？`)
  if (!confirm) return
  
  try {
    const res = await axios.post('/api/item/batch/archive', {
      itemIds: selectedItems.value,
      archiveDesc: '管理员批量归档',
      archiveType: '批量处理'
    })
    
    if (res.data.code === 200) {
      selectedItems.value = []
      await loadItemList()
      await loadUnclaimedStats()
    }
  } catch (error) {
    console.error('批量归档失败:', error)
    alert('操作失败，请重试')
  }
}

/* ================= 认领申请审核 ================= */
const viewClaims = async (item: any) => {
  claimsItem.value = item
  showClaimsModal.value = true
  
  try {
    const res = await axios.get('/api/item/claim/list', {
      params: { itemId: item.itemId, page: 1, size: 100 }
    })
    
    if (res.data.code === 200) {
      claimsList.value = res.data.data.list || []
    }
  } catch (error) {
    console.error('加载认领申请失败:', error)
    claimsList.value = []
  }
}

const closeClaimsModal = () => {
  showClaimsModal.value = false
  claimsItem.value = null
  claimsList.value = []
}

const auditClaim = async (claimId: number, status: number) => {
  try {
    const res = await axios.post(`/api/item/claim/${claimId}/audit`, { status })
    
    if (res.data.code === 200) {
      // 刷新认领列表和物品列表
      await viewClaims(claimsItem.value)
      await loadItemList()
    }
  } catch (error) {
    console.error('审核认领申请失败:', error)
    alert('操作失败，请重试')
  }
}

/* ================= 长期未认领物品 ================= */
const openUnclaimedModal = async () => {
  showUnclaimedModal.value = true
  
  try {
    const res = await axios.get('/api/item/unclaimed/long-term', {
      params: { days: 30, page: 1, size: 100 }
    })
    
    if (res.data.code === 200) {
      unclaimedList.value = res.data.data.list || []
    }
  } catch (error) {
    console.error('加载未认领物品失败:', error)
    unclaimedList.value = []
  }
}

const closeUnclaimedModal = () => {
  showUnclaimedModal.value = false
  unclaimedList.value = []
}

const quickArchive = (item: any) => {
  closeUnclaimedModal()
  openArchiveModal(item)
}

const batchArchiveUnclaimed = async () => {
  if (unclaimedList.value.length === 0) return
  
  const confirm = window.confirm(`确定要批量归档 ${unclaimedList.value.length} 个长期未认领物品吗？`)
  if (!confirm) return
  
  const itemIds = unclaimedList.value.map(item => item.itemId)
  
  try {
    const res = await axios.post('/api/item/batch/archive', {
      itemIds,
      archiveDesc: '超过30天无人认领，系统自动归档',
      archiveType: '超期归档'
    })
    
    if (res.data.code === 200) {
      closeUnclaimedModal()
      await loadItemList()
      await loadUnclaimedStats()
    }
  } catch (error) {
    console.error('批量归档失败:', error)
    alert('操作失败，请重试')
  }
}

/* ================= 删除 ================= */
const confirmDelete = (item: any) => {
  deletingItem.value = item
  showDeleteModal.value = true
}

const closeDeleteModal = () => {
  showDeleteModal.value = false
  deletingItem.value = null
}

const confirmDeleteItem = async () => {
  if (!deletingItem.value) return
  
  try {
    const res = await axios.delete(`/api/item/${deletingItem.value.itemId}/delete`)
    
    if (res.data.code === 200) {
      await loadItemList()
      closeDeleteModal()
    }
  } catch (error) {
    console.error('删除失败:', error)
    alert('操作失败，请重试')
  }
}

const batchDelete = async () => {
  if (selectedItems.value.length === 0) return
  
  const confirm = window.confirm(`确定要删除 ${selectedItems.value.length} 个物品吗？此操作不可恢复！`)
  if (!confirm) return
  
  // 逐个删除
  try {
    for (const itemId of selectedItems.value) {
      await axios.delete(`/api/item/${itemId}/delete`)
    }
    selectedItems.value = []
    await loadItemList()
  } catch (error) {
    console.error('批量删除失败:', error)
    alert('操作失败，请重试')
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
const getStatusClass = (status: number) => {
  const classMap: Record<number, string> = {
    1: 'status-pending',
    2: 'status-approved',
    3: 'status-matched',
    4: 'status-claimed',
    5: 'status-rejected',
    6: 'status-canceled',
    7: 'status-archived'
  }
  return classMap[status] || ''
}

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
  if (diff < 2592000) return `${Math.floor(diff / 86400)}天前`
  return `${Math.floor(diff / 2592000)}个月前`
}

const maskPhone = (phone: string) => {
  if (!phone || phone.length !== 11) return phone
  return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2')
}

const truncateText = (text: string, length: number) => {
  if (!text) return ''
  return text.length > length ? text.substring(0, length) + '...' : text
}

/* ================= 生命周期 ================= */
onMounted(() => {
  loadItemList()
  loadUnclaimedStats()
})
</script>

<style scoped>
/* 基础布局 */
.item-manage-page {
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

.stat-card.highlight {
  border-color: rgba(76, 175, 80, 0.4);
}

.stat-card.warning {
  border-color: rgba(255, 152, 0, 0.4);
}

.stat-card.success {
  border-color: rgba(33, 150, 243, 0.4);
}

.stat-card.danger {
  border-color: rgba(244, 67, 54, 0.4);
}

.stat-card.info {
  border-color: rgba(156, 39, 176, 0.4);
}

.stat-icon {
  font-size: 28px;
  margin-bottom: 8px;
}

.stat-value {
  font-family: "Comic Sans MS", "Marker Felt", cursive;
  font-size: 24px;
  color: #a67c52;
  font-weight: 700;
  margin-bottom: 5px;
}

.stat-label {
  font-family: "Comic Sans MS", cursive;
  font-size: 13px;
  color: rgba(166, 124, 82, 0.7);
}

/* 工具栏 */
.toolbar-section {
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(15px);
  border-radius: 16px;
  padding: 20px;
  border: 2px solid rgba(166, 124, 82, 0.2);
  margin-bottom: 20px;
}

.filter-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  flex-wrap: wrap;
  gap: 15px;
}

.filter-group {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
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

.search-box {
  display: flex;
  gap: 8px;
}

.search-input {
  width: 250px;
  padding: 10px 15px;
  border: 1.6px solid rgba(166, 124, 82, 0.4);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.4);
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
  outline: none;
}

.search-input::placeholder {
  color: rgba(166, 124, 82, 0.5);
}

.search-btn {
  padding: 10px 15px;
  border: none;
  border-radius: 10px;
  background: linear-gradient(to right, #f38181, #f77d5f);
  color: white;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.search-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(243, 129, 129, 0.3);
}

.action-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 15px;
  border-top: 1px solid rgba(166, 124, 82, 0.1);
}

.batch-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.selected-count {
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
  font-weight: 600;
}

.batch-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 8px;
  font-family: "Comic Sans MS", cursive;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.batch-btn.archive-btn {
  background: linear-gradient(to right, #ff9800, #f57c00);
  color: white;
}

.batch-btn.delete-btn {
  background: linear-gradient(to right, #f44336, #d32f2f);
  color: white;
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

/* 加载和空状态 */
.loading-container,
.empty-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 0;
  text-align: center;
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

.row-selected {
  background: rgba(243, 129, 129, 0.1) !important;
}

.col-checkbox { width: 40px; }
.col-id { width: 60px; }
.col-type { width: 80px; }
.col-image { width: 80px; }
.col-info { min-width: 150px; }
.col-status { width: 120px; }
.col-claims { width: 120px; }
.col-time { width: 120px; }
.col-actions { min-width: 200px; }

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

/* 状态标签 */
.status-tag {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 600;
  color: white;
  margin-bottom: 4px;
}

.status-pending { background: #ff9800; }
.status-approved { background: #4caf50; }
.status-matched { background: #2196f3; }
.status-claimed { background: #9c27b0; }
.status-rejected { background: #f44336; }
.status-canceled { background: #9e9e9e; }
.status-archived { background: #795548; }

.archive-desc {
  font-size: 11px;
  color: rgba(166, 124, 82, 0.7);
  cursor: help;
}

/* 认领申请 */
.claim-badge {
  display: inline-block;
  padding: 4px 10px;
  background: linear-gradient(to right, #ff9800, #f57c00);
  color: white;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.claim-badge:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(255, 152, 0, 0.3);
}

.claim-info {
  font-size: 12px;
  color: rgba(166, 124, 82, 0.7);
}

.claim-empty {
  color: rgba(166, 124, 82, 0.4);
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

.status-btn {
  background: linear-gradient(to right, #2196f3, #21cbf3);
  color: white;
}

.claim-btn {
  background: linear-gradient(to right, #ff9800, #ffc107);
  color: white;
}

.archive-btn {
  background: linear-gradient(to right, #795548, #8d6e63);
  color: white;
}

.delete-btn {
  background: linear-gradient(to right, #f44336, #ef5350);
  color: white;
}

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
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

/* 模态框样式（复用之前的，略作调整） */
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

/* 状态更新弹窗特有样式 */
.status-modal {
  background: white;
  border-radius: 20px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.current-item {
  background: rgba(166, 124, 82, 0.1);
  padding: 15px;
  border-radius: 12px;
  margin-bottom: 20px;
}

.item-name {
  font-family: "Comic Sans MS", cursive;
  font-size: 16px;
  color: #a67c52;
  font-weight: 600;
  display: block;
  margin-bottom: 5px;
}

.current-status {
  font-family: "Comic Sans MS", cursive;
  font-size: 13px;
  color: rgba(166, 124, 82, 0.7);
}

.status-options {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 20px;
}

.status-option {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  border: 2px solid rgba(166, 124, 82, 0.2);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.status-option:hover {
  border-color: rgba(243, 129, 129, 0.4);
  background: rgba(243, 129, 129, 0.05);
}

.status-option.active {
  border-color: #f38181;
  background: rgba(243, 129, 129, 0.1);
}

.status-icon {
  font-size: 24px;
}

.status-info {
  flex: 1;
}

.status-name {
  font-family: "Comic Sans MS", cursive;
  font-size: 15px;
  color: #a67c52;
  font-weight: 600;
  margin-bottom: 3px;
}

.status-desc {
  font-family: "Comic Sans MS", cursive;
  font-size: 12px;
  color: rgba(166, 124, 82, 0.7);
}

/* 归档弹窗 */
.archive-modal {
  background: white;
  border-radius: 20px;
  width: 90%;
  max-width: 450px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.archive-item {
  text-align: center;
  margin-bottom: 20px;
}

.archive-types {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 15px;
}

.type-btn {
  padding: 8px 16px;
  border: 1.6px solid rgba(166, 124, 82, 0.4);
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.4);
  font-family: "Comic Sans MS", cursive;
  font-size: 13px;
  color: #a67c52;
  cursor: pointer;
  transition: all 0.3s ease;
}

.type-btn:hover,
.type-btn.active {
  border-color: #f38181;
  background: linear-gradient(to right, #f38181, #f77d5f);
  color: white;
}

/* 认领申请弹窗 */
.claims-modal {
  background: white;
  border-radius: 20px;
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.claims-item-info {
  display: flex;
  gap: 15px;
  align-items: center;
  background: rgba(166, 124, 82, 0.1);
  padding: 15px;
  border-radius: 12px;
  margin-bottom: 20px;
}

.claims-item-image {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  object-fit: cover;
}

.claims-item-name {
  font-family: "Comic Sans MS", cursive;
  font-size: 16px;
  color: #a67c52;
  font-weight: 600;
}

.claims-item-status {
  font-family: "Comic Sans MS", cursive;
  font-size: 13px;
  color: rgba(166, 124, 82, 0.7);
}

.claims-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.claim-card {
  border: 1.6px solid rgba(166, 124, 82, 0.2);
  border-radius: 12px;
  padding: 15px;
  background: rgba(255, 255, 255, 0.5);
}

.claim-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.claim-user {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(to right, #f38181, #f77d5f);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: "Comic Sans MS", cursive;
  font-size: 16px;
  font-weight: 600;
}

.user-name {
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
  font-weight: 600;
}

.user-phone {
  font-family: "Comic Sans MS", cursive;
  font-size: 12px;
  color: rgba(166, 124, 82, 0.7);
}

.claim-status {
  padding: 4px 10px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 600;
  color: white;
}

.claim-status.status-0 { background: #ff9800; }
.claim-status.status-1 { background: #4caf50; }
.claim-status.status-2 { background: #f44336; }

.claim-content {
  margin-bottom: 10px;
}

.claim-label {
  font-family: "Comic Sans MS", cursive;
  font-size: 12px;
  color: rgba(166, 124, 82, 0.7);
  margin-bottom: 4px;
}

.claim-proof {
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
  background: rgba(166, 124, 82, 0.1);
  padding: 10px;
  border-radius: 8px;
}

.claim-time {
  font-family: "Comic Sans MS", cursive;
  font-size: 12px;
  color: rgba(166, 124, 82, 0.6);
  margin-bottom: 12px;
}

.claim-actions {
  display: flex;
  gap: 10px;
}

.claim-btn {
  flex: 1;
  padding: 10px;
  border: none;
  border-radius: 8px;
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.claim-btn.approve {
  background: linear-gradient(to right, #4caf50, #8bc34a);
  color: white;
}

.claim-btn.reject {
  background: linear-gradient(to right, #f44336, #ef5350);
  color: white;
}

/* 长期未认领弹窗 */
.unclaimed-modal {
  background: white;
  border-radius: 20px;
  width: 90%;
  max-width: 500px;
  max-height: 70vh;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.unclaimed-list {
  max-height: 50vh;
  overflow-y: auto;
}

.unclaimed-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  border-bottom: 1px solid rgba(166, 124, 82, 0.1);
}

.unclaimed-item:last-child {
  border-bottom: none;
}

.item-info {
  flex: 1;
}

.item-name {
  font-family: "Comic Sans MS", cursive;
  font-size: 15px;
  color: #a67c52;
  font-weight: 600;
  margin-bottom: 4px;
}

.item-location,
.item-time {
  font-family: "Comic Sans MS", cursive;
  font-size: 12px;
  color: rgba(166, 124, 82, 0.7);
}

.quick-archive-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 8px;
  background: linear-gradient(to right, #f38181, #f77d5f);
  color: white;
  font-family: "Comic Sans MS", cursive;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.quick-archive-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(243, 129, 129, 0.3);
}

/* 表单样式 */
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

.form-input,
.form-textarea {
  width: 100%;
  padding: 12px;
  border: 1.6px solid rgba(166, 124, 82, 0.4);
  border-radius: 10px;
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
  outline: none;
  box-sizing: border-box;
}

.form-input:focus,
.form-textarea:focus {
  border-color: rgba(243, 129, 129, 0.7);
  box-shadow: 0 0 0 3px rgba(243, 129, 129, 0.1);
}

/* 确认弹窗 */
.confirm-modal {
  background: white;
  border-radius: 20px;
  width: 90%;
  max-width: 400px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.confirm-content {
  text-align: center;
  padding: 20px;
}

.confirm-icon {
  font-size: 48px;
  margin-bottom: 15px;
}

.confirm-text {
  font-family: "Comic Sans MS", cursive;
  font-size: 16px;
  color: #a67c52;
  margin-bottom: 10px;
}

.confirm-hint {
  font-family: "Comic Sans MS", cursive;
  font-size: 13px;
  color: #f44336;
}

/* 按钮样式 */
.cancel-btn {
  background: rgba(166, 124, 82, 0.1);
  color: #a67c52;
  border: 1px solid rgba(166, 124, 82, 0.3);
}

.confirm-btn {
  background: linear-gradient(to right, #2196f3, #21cbf3);
  color: white;
}

.archive-confirm-btn {
  background: linear-gradient(to right, #795548, #8d6e63);
  color: white;
}

.delete-confirm-btn {
  background: linear-gradient(to right, #f44336, #ef5350);
  color: white;
}

.batch-archive-btn {
  background: linear-gradient(to right, #ff9800, #f57c00);
  color: white;
}

/* 图片预览 */
.image-preview {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  border: 1px solid rgba(166, 124, 82, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  overflow: hidden;
}

.image-preview:hover {
  border-color: rgba(243, 129, 129, 0.5);
  transform: scale(1.05);
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
    grid-template-columns: repeat(3, 1fr);
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
    padding: 15px 10px;
  }

  .stat-value {
    font-size: 20px;
  }

  .filter-row {
    flex-direction: column;
    align-items: stretch;
  }

  .search-input {
    width: 100%;
  }

  .action-row {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }

  .data-table th,
  .data-table td {
    padding: 10px 8px;
    font-size: 12px;
  }

  .col-checkbox,
  .col-id {
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
}
</style>