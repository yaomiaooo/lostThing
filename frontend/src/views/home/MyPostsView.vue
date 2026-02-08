<template>
  <div class="my-posts-page">
    <!-- 纯色背景 -->
    <div class="background-container">
      <div class="solid-background"></div>
    </div>

    <!-- 整体布局：左侧导航 + 右侧主内容 -->
    <div class="layout-container">
      <!-- 左侧导航栏（与首页一致） -->
      <aside class="left-nav">
        <!-- 用户信息区域 -->
        <div class="user-info-container">
          <div class="user-avatar-container">
            <img class="user-avatar" src="/home/avatar.png" />
            <div class="user-avatar-border"></div>
          </div>
          <div class="user-text">
            <div class="user-nickname">{{ user.realName }}</div>
            <div class="user-subtitle">欢迎回来^_^</div>
          </div>
        </div>

        <!-- 左侧上半区：核心导航 -->
        <div class="nav-top-group">
          <button 
            v-for="nav in navItems" 
            :key="nav.name"
            class="left-nav-btn"
            :class="{ active: nav.name === '我的' }"
            @click="nav.handler"
          >
            <span class="nav-icon">
              <img :src="nav.icon" :alt="nav.name" class="nav-svg" />
            </span>
            <span class="nav-text">{{ nav.name }}</span>
          </button>
        </div>

        <!-- 左侧中间：统计卡片 -->
        <div class="left-notice-card bubble">
          <div class="notice-content">
            <div class="notice-title">📊 发布统计</div>
            <div class="stat-item">
              <span class="stat-label">总发布数：</span>
              <span class="stat-value">{{ stats.total }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">待审核：</span>
              <span class="stat-value pending">{{ stats.pending }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">已通过：</span>
              <span class="stat-value approved">{{ stats.approved }}</span>
            </div>
          </div>
          <div class="notice-time">今日更新</div>
        </div>

        <!-- 左侧下半区：操作按钮 -->
        <div class="nav-bottom-group">
          <button 
            class="left-action-btn back-btn"
            @click="goBack"
          >
            <span class="btn-text">返回首页</span>
          </button>
          <button 
            class="left-action-btn logout-btn"
            @click="logout"
          >
            <span class="btn-text">退出登录</span>
          </button>
        </div>
      </aside>

      <!-- 右侧主内容区域 -->
      <main class="main-content">
        <!-- 页面标题和操作区 -->
        <section class="page-header">
          <div class="header-left">
            <h1 class="page-title">我的发布</h1>
            <div class="subtitle">管理您的所有失物/招领记录</div>
          </div>
          <div class="header-right">
            <button class="new-post-btn" @click="goPublish">
              <span class="btn-icon">+</span>
              <span class="btn-text">发布新物品</span>
            </button>
          </div>
        </section>

        <!-- 状态筛选标签 -->
        <section class="status-filter-section">
          <div class="status-filter-tabs">
            <button 
              class="status-tab" 
              :class="{ active: currentStatus === 'all' }"
              @click="setStatusFilter('all')"
            >
              全部 ({{ stats.total }})
            </button>
            <button 
              class="status-tab" 
              :class="{ active: currentStatus === '1' }"
              @click="setStatusFilter('1')"
            >
              待审核 ({{ stats.pending }})
            </button>
            <button 
              class="status-tab" 
              :class="{ active: currentStatus === '2' }"
              @click="setStatusFilter('2')"
            >
              已通过 ({{ stats.approved }})
            </button>
            <button 
              class="status-tab" 
              :class="{ active: currentStatus === '3' }"
              @click="setStatusFilter('3')"
            >
              已匹配 ({{ stats.matched }})
            </button>
            <button 
              class="status-tab" 
              :class="{ active: currentStatus === '4' }"
              @click="setStatusFilter('4')"
            >
              已认领 ({{ stats.claimed }})
            </button>
            <button 
              class="status-tab" 
              :class="{ active: currentStatus === '5' }"
              @click="setStatusFilter('5')"
            >
              已驳回 ({{ stats.rejected }})
            </button>
            <button 
              class="status-tab" 
              :class="{ active: currentStatus === '6' }"
              @click="setStatusFilter('6')"
            >
              已取消 ({{ stats.canceled }})
            </button>
          </div>
        </section>

        <!-- 物品列表 -->
        <section class="posts-list-section">
          <!-- 加载状态 -->
          <div v-if="loading" class="loading-container">
            <div class="loading-spinner"></div>
            <div class="loading-text">加载中...</div>
          </div>

          <!-- 空状态 -->
          <div v-else-if="filteredPosts.length === 0" class="empty-container">
            <div class="empty-icon">📭</div>
            <div class="empty-title">暂无发布记录</div>
            <div class="empty-desc">快去发布您的第一条失物/招领信息吧！</div>
            <button class="empty-action-btn" @click="goPublish">
              发布新物品
            </button>
          </div>

          <!-- 发布记录列表 - 瀑布流布局 -->
          <div v-else class="waterfall-grid">
            <div 
              v-for="post in filteredPosts" 
              :key="post.itemId"
              class="waterfall-card"
              :class="post.itemCategory === 1 ? 'lost-card' : 'found-card'"
            >
              <!-- 显示图片 -->
              <img
                v-if="post.firstImageUrl"
                class="card-image"
                :src="post.firstImageUrl"
                :alt="post.name"
                @error="handleImageError"
              />
              <div class="card-tag" :class="post.itemCategory === 1 ? 'lost-tag' : 'found-tag'">
                {{ post.itemCategory === 1 ? '失物' : '招领' }}
              </div>

              <div class="card-content">
                <div class="card-name">{{ post.name }}</div>
                <div class="card-info">
                <span class="info-item campus">🏫 {{ getCampusName(post.locationId) }}</span>
                <span class="info-item">📍 {{ post.locationName }}</span>
              </div>
                
                

                <!-- 状态标签 -->
                <div class="post-status" :class="getStatusClass(post.currentStatus)">
                  {{ getStatusText(post.currentStatus) }}
                </div>

                <!-- 驳回原因（如果状态是已驳回） -->
                <div v-if="post.currentStatus === 5 && post.rejectReason" class="reject-reason">
                  <div class="reject-title">驳回原因：</div>
                  <div class="reject-content">{{ post.rejectReason }}</div>
                </div>

                <!-- 操作按钮区域 -->
                <div class="post-actions">
                  <!-- 待审核状态：修改、删除 -->
                  <template v-if="post.currentStatus === 1">
                    <button class="action-btn edit-btn" @click.stop="editPost(post)">
                      修改
                    </button>
                    <button class="action-btn delete-btn" @click.stop="confirmDelete(post)">
                      删除
                    </button>
                  </template>

                  <!-- 已通过状态：取消发布 -->
                  <template v-else-if="post.currentStatus === 2">
                    <button class="action-btn cancel-btn" @click.stop="confirmCancel(post)">
                      取消发布
                    </button>
                  </template>

                  <!-- 已驳回状态：修改、删除 -->
                  <template v-else-if="post.currentStatus === 5">
                    <button class="action-btn edit-btn" @click.stop="editPost(post)">
                      重新编辑
                    </button>
                    <button class="action-btn delete-btn" @click.stop="confirmDelete(post)">
                      删除
                    </button>
                  </template>

                  <!-- 已取消状态：删除 -->
                  <template v-else-if="post.currentStatus === 6">
                    <button class="action-btn delete-btn" @click.stop="confirmDelete(post)">
                      删除
                    </button>
                  </template>

                  <!-- 查看详情按钮（所有状态） -->
                  <button class="action-btn detail-btn" @click.stop="viewDetail(post)">
                    查看详情
                  </button>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>

    <!-- 修改/编辑模态框 -->
    <div v-if="showEditModal" class="modal-overlay">
      <div class="edit-modal">
        <div class="modal-header">
          <h3 class="modal-title">{{ editingPost.itemCategory === 1 ? '修改失物信息' : '修改招领信息' }}</h3>
          <button class="modal-close" @click="closeEditModal">×</button>
        </div>
        <div class="modal-content">
          <form @submit.prevent="submitEdit">
            <div class="form-group">
              <label class="form-label">物品名称 *</label>
              <input
                v-model="editingPost.name"
                type="text"
                class="form-input"
                placeholder="请输入物品名称"
                required
              />
            </div>
            <div class="form-group">
              <label class="form-label">物品分类 *</label>
              <select v-model="editingPost.itemCategory" class="form-select" required @change="handleCategoryChange">
                <option value="1">失物</option>
                <option value="2">招领</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">物品类型 *</label>
              <select v-model="editingPost.itemType" class="form-select" required>
                <option value="">请选择类型</option>
                <optgroup v-for="category in categoryTree" :key="category.id" :label="category.name">
                  <option 
                    v-for="sub in category.children" 
                    :key="sub.id" 
                    :value="sub.id"
                  >
                    {{ sub.name }}
                  </option>
                </optgroup>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">校区 *</label>
              <select v-model="editingPost.campus" class="form-select" required @change="filterLocationOptions">
                <option value="">请选择校区</option>
                <option value="1">朝晖校区</option>
                <option value="2">屏峰校区</option>
                <option value="3">莫干山校区</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">具体地点 *</label>
              <select v-model="editingPost.locationId" class="form-select" required>
                <option value="">请选择具体地点</option>
                <option v-for="location in locationOptions" :key="location.id" :value="location.id">
                  {{ location.name }}
                </option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">详细位置描述</label>
              <input
                v-model="editingPost.locationDetail"
                type="text"
                class="form-input"
                placeholder="例如：图书馆三楼自习区靠窗位置"
              />
            </div>
            <div class="form-group">
              <label class="form-label">领取地点</label>
              <input
                v-model="editingPost.pickupLocation"
                type="text"
                class="form-input"
                placeholder="例如：校保卫处值班室"
              />
            </div>
            <div class="form-group">
              <label class="form-label">物品描述 *</label>
              <textarea
                v-model="editingPost.feature"
                class="form-textarea"
                placeholder="请详细描述物品特征、颜色、品牌等信息..."
                rows="3"
                required
              ></textarea>
            </div>
            <div class="form-group">
              <label class="form-label">发生时间 *</label>
              <input
                v-model="editingPost.happenTime"
                type="datetime-local"
                class="form-input"
                required
              />
            </div>
            <div class="form-group">
              <label class="form-label">悬赏金额（元）</label>
              <input
                v-model.number="editingPost.rewardAmount"
                type="number"
                class="form-input"
                placeholder="0"
                min="0"
                :disabled="editingPost.itemCategory == 2"
              />
              <small v-if="editingPost.itemCategory == 2" class="form-hint">招领信息不能设置悬赏</small>
            </div>
            <div class="form-group">
              <label class="form-label">悬赏描述</label>
              <input
                v-model="editingPost.rewardDesc"
                type="text"
                class="form-input"
                placeholder="例如：找到必谢"
                :disabled="editingPost.itemCategory == 2"
              />
            </div>
            <div class="form-group">
              <label class="form-label">联系人姓名 *</label>
              <input
                v-model="editingPost.contactName"
                type="text"
                class="form-input"
                placeholder="请输入联系人姓名"
                required
              />
            </div>
            <div class="form-group">
              <label class="form-label">联系电话 *</label>
              <input
                v-model="editingPost.contactPhone"
                type="tel"
                class="form-input"
                placeholder="请输入联系电话"
                pattern="[0-9]{11}"
                required
              />
            </div>
            <div class="modal-actions">
              <button type="button" class="modal-btn cancel-btn" @click="closeEditModal">
                取消
              </button>
              <button type="submit" class="modal-btn submit-btn" :disabled="submitting">
                {{ submitting ? '提交中...' : '确认修改' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- 确认删除模态框 -->
    <div v-if="showDeleteConfirm" class="modal-overlay">
      <div class="confirm-modal">
        <div class="modal-header">
          <h3 class="modal-title">确认删除</h3>
          <button class="modal-close" @click="closeDeleteConfirm">×</button>
        </div>
        <div class="modal-content">
          <p>确定要删除"{{ deletingPost?.name }}"这条记录吗？删除后不可恢复。</p>
          <div class="modal-actions">
            <button type="button" class="modal-btn cancel-btn" @click="closeDeleteConfirm">
              取消
            </button>
            <button type="button" class="modal-btn delete-confirm-btn" @click="deletePost">
              确认删除
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 确认取消发布模态框 -->
    <div v-if="showCancelConfirm" class="modal-overlay">
      <div class="confirm-modal">
        <div class="modal-header">
          <h3 class="modal-title">确认取消发布</h3>
          <button class="modal-close" @click="closeCancelConfirm">×</button>
        </div>
        <div class="modal-content">
          <p>确定要取消发布"{{ cancelingPost?.name }}"这条记录吗？</p>
          <div class="modal-actions">
            <button type="button" class="modal-btn cancel-btn" @click="closeCancelConfirm">
              不取消
            </button>
            <button type="button" class="modal-btn cancel-confirm-btn" @click="cancelPost">
              确认取消
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 物品详情卡片 -->
    <ItemDetailView
      :visible="showItemDetail"
      :itemId="currentItemId"
      :show-actions="true"
      @close="handleDetailClose"
      @edit="handleDetailEdit"
      @delete="handleDetailDelete"
      @cancel="handleDetailCancel"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import ItemDetailView from './ItemDetailView.vue'

const router = useRouter()

/* ================= 用户信息 ================= */
const user = ref({
  id: 0,
  username: '',
  realName: '加载中...',
  phone: '',
  role: 0,
  status: 0
})

/* ================= 发布记录数据 ================= */
const myPosts = ref<any[]>([])
const loading = ref(false)
const currentStatus = ref('all') // 当前筛选状态

/* ================= 统计信息 ================= */
const stats = reactive({
  total: 0,
  pending: 0,
  approved: 0,
  matched: 0,
  claimed: 0,
  rejected: 0,
  canceled: 0
})

/* ================= 模态框状态 ================= */
const showEditModal = ref(false)
const showDeleteConfirm = ref(false)
const showCancelConfirm = ref(false)

const editingPost = ref<any>(null)
const deletingPost = ref<any>(null)
const cancelingPost = ref<any>(null)
const submitting = ref(false)

/* ================= 物品详情卡片状态 ================= */
const showItemDetail = ref(false)
const currentItemId = ref<number | null>(null)

/* ================= 分类数据和地点数据 ================= */
const categoryTree = ref<any[]>([])
const locationTree = ref<any[]>([])
const locationOptions = ref<any[]>([])

/* ================= 左侧导航栏 ================= */
const navItems = [
  {
    name: '发现',
    icon: '/home/发现.svg',
    handler: () => router.push('/home')
  },
  {
    name: '发布',
    icon: '/home/发布.svg',
    handler: goPublish
  },
  {
    name: '消息',
    icon: '/home/消息.svg',
    handler: () => router.push('/messages')
  },
  {
    name: '我的',
    icon: '/home/我的.svg',
    handler: () => {} // 当前页面
  },
  {
    name: '设置',
    icon: '/home/设置.svg',
    handler: () => router.push('/settings')
  }
]

/* ================= 工具函数 ================= */
function getCampusName(locationId: number): string {
  const campusCode = Math.floor(locationId / 10000)
  switch (campusCode) {
    case 1:
      return '朝晖校区'
    case 2:
      return '屏峰校区'
    case 3:
      return '莫干山校区'
    default:
      return '未知校区'
  }
}

/* ================= 计算属性 ================= */
const filteredPosts = computed(() => {
  if (currentStatus.value === 'all') {
    return myPosts.value
  }
  return myPosts.value.filter(post => post.currentStatus === parseInt(currentStatus.value))
})

/* ================= 生命周期 ================= */
onMounted(() => {
  loadUser()
  loadMyPosts()
  loadCategoryTree()
  loadLocationTree()
})

/* ================= 数据加载 ================= */
async function loadUser() {
  try {
    const res = await axios.get('/api/user/info')
    if (res.data.code === 0) {
      user.value = res.data.data
    }
  } catch (error) {
    console.error('加载用户信息失败:', error)
    // 模拟数据
    user.value = {
      id: 1,
      username: '2023123456',
      realName: '齐司礼',
      phone: '13800000001',
      role: 1,
      status: 1
    }
  }
}

async function loadMyPosts() {
  loading.value = true
  try {
    // 使用我们实现的接口
    const res = await axios.get('/api/item/my-posts')
    console.log('我的发布接口返回:', res.data)
    
    if (res.data.code === 200) {
      myPosts.value = res.data.data.list || []
      // 更新统计信息
      if (res.data.data.statistics) {
        Object.assign(stats, res.data.data.statistics)
      } else {
        updateStatistics()
      }
    }
  } catch (error) {
    console.error('加载发布记录失败:', error)
    // 模拟数据
    myPosts.value = [
      {
        itemId: 1,
        name: '黑色蓝牙耳机',
        itemCategory: 1,
        itemType: 2,
        locationId: 20105,
        locationName: '健行楼 A 楼',
        feature: '右耳有划痕',
        rewardAmount: 50,
        currentStatus: 1,
        happenTime: '2026-02-01 14:30:00',
        createTime: '2026-02-01 14:30:00',
        firstImageUrl: null
      }
    ]
    updateStatistics()
  } finally {
    loading.value = false
  }
}

async function loadCategoryTree() {
  try {
    const res = await axios.get('/api/item/category/tree')
    if (res.data.code === 200) {
      categoryTree.value = res.data.data
    }
  } catch (error) {
    console.error('加载分类树失败:', error)
    // 使用默认数据
    categoryTree.value = [
      {
        id: 1,
        name: '证件',
        children: [
          { id: 101, name: '校园卡' },
          { id: 102, name: '身份证' },
          { id: 103, name: '学生证' },
          { id: 104, name: '银行卡' }
        ]
      },
      {
        id: 2,
        name: '电子设备',
        children: [
          { id: 201, name: '手机' },
          { id: 202, name: '耳机' },
          { id: 203, name: '平板电脑' },
          { id: 204, name: '充电宝' },
          { id: 205, name: '电脑' }
        ]
      },
      {
        id: 3,
        name: '日用品',
        children: [
          { id: 301, name: '水杯' },
          { id: 302, name: '雨伞' },
          { id: 303, name: '衣物' },
          { id: 304, name: '钥匙' }
        ]
      },
      {
        id: 4,
        name: '学习用品',
        children: [
          { id: 401, name: '书本' },
          { id: 402, name: '笔记本' },
          { id: 403, name: '文具' }
        ]
      },
      {
        id: 5,
        name: '其他',
        children: [
          { id: 501, name: '其他物品' }
        ]
      }
    ]
  }
}

async function loadLocationTree() {
  try {
    const res = await axios.get('/api/item/location/tree')
    if (res.data.code === 200) {
      locationTree.value = res.data.data
    }
  } catch (error) {
    console.error('加载地点树失败:', error)
  }
}

function filterLocationOptions() {
  if (!editingPost.value?.campus || !locationTree.value) {
    locationOptions.value = []
    return
  }
  
  const campusCode = parseInt(editingPost.value.campus)
  locationOptions.value = []
  
  // 遍历地点树，筛选出对应校区的所有地点
  const findLocations = (nodes: any[]) => {
    for (const node of nodes) {
      if (node.id && Math.floor(node.id / 10000) === campusCode) {
        locationOptions.value.push(node)
      }
      if (node.children) {
        findLocations(node.children)
      }
    }
  }
  
  findLocations(locationTree.value)
}

/* ================= 工具函数 ================= */
function updateStatistics() {
  const posts = myPosts.value
  stats.total = posts.length
  stats.pending = posts.filter(p => p.currentStatus === 1).length
  stats.approved = posts.filter(p => p.currentStatus === 2).length
  stats.matched = posts.filter(p => p.currentStatus === 3).length
  stats.claimed = posts.filter(p => p.currentStatus === 4).length
  stats.rejected = posts.filter(p => p.currentStatus === 5).length
  stats.canceled = posts.filter(p => p.currentStatus === 6).length
}

function getStatusText(status: number): string {
  const statusMap: Record<number, string> = {
    1: '待审核',
    2: '已通过',
    3: '已匹配',
    4: '已认领',
    5: '已驳回',
    6: '已取消'
  }
  return statusMap[status] || '未知状态'
}

function getStatusClass(status: number): string {
  const statusClassMap: Record<number, string> = {
    1: 'status-pending',
    2: 'status-approved',
    3: 'status-matched',
    4: 'status-claimed',
    5: 'status-rejected',
    6: 'status-canceled'
  }
  return statusClassMap[status] || ''
}

function formatTime(timeStr: string): string {
  if (!timeStr) return ''
  try {
    // 处理不同的时间格式
    let dateStr = timeStr
    if (timeStr.includes('T')) {
      dateStr = timeStr.replace('T', ' ')
    }
    if (dateStr.includes('.')) {
      dateStr = dateStr.split('.')[0]
    }
    
    const date = new Date(dateStr)
    const month = date.getMonth() + 1
    const day = date.getDate()
    const hours = date.getHours()
    const minutes = date.getMinutes().toString().padStart(2, '0')
    return `${month}月${day}日 ${hours}:${minutes}`
  } catch (error) {
    return timeStr
  }
}

function handleImageError(event: Event) {
  const img = event.target as HTMLImageElement
  img.src = '/home/默认.jpg'
}

/* ================= 筛选功能 ================= */
function setStatusFilter(status: string) {
  currentStatus.value = status
}

/* ================= 操作函数 ================= */
function editPost(post: any) {
  // 跳转到发布页面进行编辑，传递物品ID作为参数
  router.push(`/publish?edit=true&itemId=${post.itemId}`)
}

function handleCategoryChange() {
  // 如果是招领信息，清空悬赏金额和描述
  if (editingPost.value.itemCategory == 2) {
    editingPost.value.rewardAmount = 0
    editingPost.value.rewardDesc = ''
  }
}

async function submitEdit() {
  if (!editingPost.value) return
  
  submitting.value = true
  try {
    // 构建更新数据 - 使用后端接口期望的字段名
    const updateData = {
      name: editingPost.value.name,
      item_category: editingPost.value.itemCategory,
      item_type: editingPost.value.itemType,
      location_id: editingPost.value.locationId,
      location_detail: editingPost.value.locationDetail,
      pickup_location: editingPost.value.pickupLocation,
      happen_time: editingPost.value.happenTime.replace('T', ' ') + ':00',
      feature: editingPost.value.feature,
      reward_amount: editingPost.value.rewardAmount || 0,
      reward_desc: editingPost.value.rewardDesc,
      contact_name: editingPost.value.contactName,
      contact_phone: editingPost.value.contactPhone
    }
    
    // 使用我们实现的PUT接口
    const res = await axios.put(`/api/item/${editingPost.value.itemId}`, updateData)
    
    if (res.data.code === 200) {
      // 重新加载数据以获取最新状态
      await loadMyPosts()
      closeEditModal()
      alert('修改成功！')
    }
  } catch (error: any) {
    console.error('修改失败:', error)
    alert(`修改失败: ${error.response?.data?.msg || '请重试'}`)
  } finally {
    submitting.value = false
  }
}

function closeEditModal() {
  showEditModal.value = false
  editingPost.value = null
  locationOptions.value = []
}

function confirmDelete(post: any) {
  deletingPost.value = post
  showDeleteConfirm.value = true
}

async function deletePost() {
  if (!deletingPost.value) return
  
  try {
    // 使用我们实现的DELETE接口
    const res = await axios.delete(`/api/item/${deletingPost.value.itemId}/delete`)
    
    if (res.data.code === 200) {
      // 从本地数据中移除
      myPosts.value = myPosts.value.filter(p => p.itemId !== deletingPost.value.itemId)
      updateStatistics()
      closeDeleteConfirm()
      alert('删除成功！')
    }
  } catch (error: any) {
    console.error('删除失败:', error)
    alert(`删除失败: ${error.response?.data?.msg || '请重试'}`)
  }
}

function closeDeleteConfirm() {
  showDeleteConfirm.value = false
  deletingPost.value = null
}

function confirmCancel(post: any) {
  cancelingPost.value = post
  showCancelConfirm.value = true
}

async function cancelPost() {
  if (!cancelingPost.value) return
  
  try {
    // 使用我们实现的取消发布接口
    const res = await axios.post(`/api/item/${cancelingPost.value.itemId}/cancel`)
    
    if (res.data.code === 200) {
      // 更新本地数据状态
      const index = myPosts.value.findIndex(p => p.itemId === cancelingPost.value.itemId)
      if (index !== -1) {
        myPosts.value[index].currentStatus = 6 // 已取消
        updateStatistics()
      }
      closeCancelConfirm()
      alert('已取消发布！')
    }
  } catch (error: any) {
    console.error('取消失败:', error)
    alert(`取消失败: ${error.response?.data?.msg || '请重试'}`)
  }
}

function closeCancelConfirm() {
  showCancelConfirm.value = false
  cancelingPost.value = null
}

function viewDetail(post: any) {
  currentItemId.value = post.itemId
  showItemDetail.value = true
}

function handleDetailClose() {
  showItemDetail.value = false
  currentItemId.value = null
}

function handleDetailEdit(itemData: any) {
  showItemDetail.value = false
  // 调用现有的编辑方法
  editPost(itemData)
}

function handleDetailDelete(itemData: any) {
  showItemDetail.value = false
  // 调用现有的删除确认方法
  confirmDelete(itemData)
}

function handleDetailCancel(itemData: any) {
  showItemDetail.value = false
  // 调用现有的取消发布确认方法
  confirmCancel(itemData)
}

/* ================= 路由跳转 ================= */
function goBack() {
  router.push('/home')
}

function goPublish() {
  router.push('/publish')
}

async function logout() {
  try {
    const userId = user.value.id
    if (userId) {
      await axios.post('/api/user/logout', { userId })
    }
  } catch (error) {
    console.error('退出登录失败:', error)
  } finally {
    localStorage.clear()
    sessionStorage.clear()
    router.replace('/login')
  }
}
</script>

<style scoped>
.my-posts-page {
  width: 100vw;
  min-height: 100vh;
  position: relative;
  overflow: hidden;
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

/* 左侧导航栏样式（与首页保持一致） */
.left-nav {
  width: 288px;
  height: 100vh;
  position: fixed;
  top: 0;
  left: 0;
  background: transparent;
  padding: 24px;
  display: flex;
  flex-direction: column;
  z-index: 10;
  box-sizing: border-box;
}

.user-info-container {
  border-radius: 12.8px;
  padding: 16px;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar-container {
  position: relative;
  width: 48px;
  height: 48px;
}

.user-avatar {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
}

.user-avatar-border {
  position: absolute;
  top: -4px;
  left: -4px;
  right: -4px;
  bottom: -4px;
  border: 2px solid rgba(243, 129, 129, 0.5);
  border-radius: 50%;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 0.8; }
}

.user-text {
  display: flex;
  flex-direction: column;
}

.user-nickname {
  font-family: "Comic Sans MS", "Marker Felt", cursive;
  font-size: 20px;
  font-weight: 600;
  color: #a67c52;
  margin-bottom: 6.4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 192px;
}

.user-subtitle {
  font-family: "Comic Sans MS", cursive;
  font-size: 17.6px;
  color: rgba(166, 124, 82, 0.7);
}

.nav-top-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 8px;
}

.left-nav-btn {
  background: transparent;
  border: none;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 16px;
  cursor: pointer;
  padding: 14.4px 10px;
  border-radius: 12.8px;
  transition: all 0.3s ease;
  font-family: "Comic Sans MS", cursive;
  color: #a67c52;
  font-size: 16px;
  font-weight: 500;
  width: 100%;
  text-align: left;
}

.left-nav-btn.active {
  background: rgba(243, 129, 129, 0.15);
  font-weight: 600;
}

.left-nav-btn:hover {
  background: rgba(255, 255, 255, 0.15);
  transform: translateX(5px);
}

.left-nav-btn .nav-icon {
  font-size: 25.6px;
  min-width: 32px;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
}

.nav-svg {
  width: 25.6px;
  height: 25.6px;
  object-fit: contain;
  filter: brightness(0.8);
}

.left-nav-btn .nav-text {
  font-size: 20px;
}

/* 统计卡片 */
.left-notice-card {
  background: rgba(255, 255, 255, 0.15);
  border-radius: 14.4px;
  padding: 16px;
  margin: 15px 0;
  border: 1.6px solid rgba(166, 124, 82, 0.2);
  display: flex;
  flex-direction: column;
  width: 85%;
  box-sizing: border-box;
}

.notice-content {
  flex: 1;
}

.notice-title {
  font-family: "Comic Sans MS", cursive;
  font-size: 18px;
  color: #a67c52;
  margin-bottom: 15px;
  font-weight: 600;
  text-align: center;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
}

.stat-label {
  color: rgba(166, 124, 82, 0.8);
}

.stat-value {
  font-weight: 600;
  color: #a67c52;
}

.stat-value.pending {
  color: #ff9800;
}

.stat-value.approved {
  color: #4caf50;
}

.notice-time {
  font-family: "Comic Sans MS", cursive;
  font-size: 12px;
  color: rgba(166, 124, 82, 0.6);
  text-align: right;
  margin-top: 10px;
}

.nav-bottom-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: auto;
}

.left-action-btn {
  height: 54.4px;
  padding: 0 25.6px;
  border-radius: 12.8px;
  font-family: "Comic Sans MS", cursive;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  border: 1.6px solid transparent;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
  color: white;
  width: 100%;
}

.left-action-btn:hover {
  transform: translateX(5px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
}

.back-btn {
  background: linear-gradient(to right, #4CAF50, #8BC34A);
  width: 75%;
}

.logout-btn {
  background: linear-gradient(to right, #f38181, #f77d5f);
  width: 75%;
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

/* 页面标题区域 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
}

.header-left {
  flex: 1;
}

.page-title {
  font-family: "Comic Sans MS", "Marker Felt", cursive;
  font-size: 36px;
  color: #a67c52;
  margin: 0 0 8px 0;
  font-weight: 700;
}

.subtitle {
  font-family: "Comic Sans MS", cursive;
  font-size: 18px;
  color: rgba(166, 124, 82, 0.7);
}

.new-post-btn {
  background: linear-gradient(to right, #f38181, #f77d5f);
  border: none;
  border-radius: 12.8px;
  padding: 14.4px 25.6px;
  color: white;
  font-family: "Comic Sans MS", cursive;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(243, 129, 129, 0.3);
}

.new-post-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(243, 129, 129, 0.4);
}

.btn-icon {
  font-size: 20px;
}

/* 状态筛选标签 */
.status-filter-section {
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(15px);
  border-radius: 20px;
  padding: 20px 25px;
  border: 2px solid rgba(166, 124, 82, 0.2);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
  margin-bottom: 25px;
}

.status-filter-tabs {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.status-tab {
  padding: 12.8px 22.4px;
  border-radius: 19.2px;
  border: none;
  background: rgba(255, 255, 255, 0.3);
  color: #a67c52;
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.status-tab.active {
  background: linear-gradient(135deg, #f38181, #f77d5f);
  color: white;
  box-shadow: 0 4px 12px rgba(243, 129, 129, 0.3);
}

.status-tab:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* 发布记录列表 */
.posts-list-section {
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
  max-width: 400px;
}

.empty-action-btn {
  background: linear-gradient(to right, #f38181, #f77d5f);
  border: none;
  border-radius: 12.8px;
  padding: 14.4px 25.6px;
  color: white;
  font-family: "Comic Sans MS", cursive;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(243, 129, 129, 0.3);
}

.empty-action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(243, 129, 129, 0.4);
}

/* 瀑布流网格 */
.waterfall-grid {
  column-count: 4;
  column-gap: 20px;
}

/* 瀑布流卡片基础样式 */
.waterfall-card {
  break-inside: avoid;
  margin-bottom: 20px;
  background: rgba(255,255,255,0.35);
  border-radius: 16px;
  overflow: hidden;
  position: relative;
  transition: 0.3s;
  display: flex;
  flex-direction: column;
}

.waterfall-card:hover {
  transform: translateY(-6px);
}

.card-image {
  width: 100%;
  height: auto;
  display: block;
}

.waterfall-card:hover .card-image {
  transform: scale(1.05);
}

.card-tag {
  position: absolute;
  top: 15px;
  right: 15px;
  padding: 6px 15px;
  border-radius: 20px;
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  font-weight: 600;
  color: white;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
}

.lost-tag {
  background: linear-gradient(135deg, #ff9a9e 0%, #fad0c4 100%);
  border: 1px solid rgba(255, 154, 158, 0.3);
}

.found-tag {
  background: linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%);
  border: 1px solid rgba(161, 196, 253, 0.3);
}

.card-content {
  padding: 25px;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.card-name {
  font-family: "Comic Sans MS", "Marker Felt", cursive;
  font-size: 17.6px;
  color: #a67c52;
  margin-bottom: 11.2px;
  font-weight: 600;
  line-height: 1.3;
}

.card-info {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: auto;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 6.4px;
  font-family: "Comic Sans MS", cursive;
  font-size: 16px;
  color: rgba(166, 124, 82, 0.8);
}

.info-icon {
  font-size: 14.4px;
}

.post-desc {
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: rgba(166, 124, 82, 0.9);
  line-height: 1.5;
  margin-bottom: 12px;
  flex: 1;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* 状态标签 */
.post-status {
  padding: 6px 12px;
  border-radius: 12px;
  font-family: "Comic Sans MS", cursive;
  font-size: 12px;
  font-weight: 600;
  color: white;
  white-space: nowrap;
  background: rgba(166, 124, 82, 0.3);
  border: 1px solid rgba(166, 124, 82, 0.2);
  margin-bottom: 12px;
  align-self: flex-start;
}

.reject-reason {
  background: rgba(244, 67, 54, 0.1);
  border: 1px solid rgba(244, 67, 54, 0.3);
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 16px;
}

.reject-title {
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #f44336;
  font-weight: 600;
  margin-bottom: 4px;
}

.reject-content {
  font-family: "Comic Sans MS", cursive;
  font-size: 13px;
  color: rgba(166, 124, 82, 0.9);
  line-height: 1.4;
}

.post-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.action-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 8px;
  font-family: "Comic Sans MS", cursive;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
  background: rgba(255, 255, 255, 0.3);
  color: #a67c52;
  border: 1px solid rgba(166, 124, 82, 0.2);
}

.action-btn:hover {
  background: rgba(255, 255, 255, 0.5);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.detail-btn {
  background: linear-gradient(to right, #f38181, #f77d5f);
  color: white;
  border: 1px solid rgba(166, 124, 82, 0.3);
}

.detail-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(247, 125, 95, 0.4);
  background: linear-gradient(to right, #f77d5f, #f38181);
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(5px);
}

.edit-modal,
.supplement-modal,
.confirm-modal {
  background: white;
  border-radius: 16px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.modal-title {
  font-family: "Comic Sans MS", cursive;
  font-size: 20px;
  color: #333;
  margin: 0;
  font-weight: 600;
}

.modal-close {
  background: none;
  border: none;
  font-size: 24px;
  color: #999;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.modal-close:hover {
  background: #f5f5f5;
  color: #666;
}

.modal-content {
  padding: 20px;
}

.form-group {
  margin-bottom: 20px;
}

.form-label {
  display: block;
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
  font-weight: 500;
}

.form-input,
.form-select,
.form-textarea {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #333;
  background: #fff;
  box-sizing: border-box;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: #f37f75;
  box-shadow: 0 0 0 2px rgba(243, 127, 117, 0.2);
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 30px;
}

.modal-btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 100px;
}

.cancel-btn {
  background: #f5f5f5;
  color: #666;
}

.cancel-btn:hover {
  background: #e0e0e0;
}

.submit-btn {
  background: #f37f75;
  color: white;
}

.submit-btn:hover:not(:disabled) {
  background: #e62e47;
  transform: translateY(-2px);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.delete-confirm-btn {
  background: #f44336;
  color: white;
}

.delete-confirm-btn:hover {
  background: #d32f2f;
}

.cancel-confirm-btn {
  background: #ff9800;
  color: white;
}

.cancel-confirm-btn:hover {
  background: #f57c00;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .layout-container {
    flex-direction: column;
  }

  .left-nav {
    width: 100%;
    height: auto;
    position: fixed;
    bottom: 0;
    left: 0;
    top: auto;
    border-right: none;
    border-top: 2px solid rgba(166, 124, 82, 0.2);
    padding: 10px 15px;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    gap: 0;
    z-index: 100;
  }

  .user-info-container,
  .left-notice-card {
    display: none;
  }

  .nav-top-group {
    flex-direction: row;
    flex: 1;
    margin-top: 0;
    justify-content: space-around;
  }

  .left-nav-btn {
    flex-direction: column;
    padding: 10px 5px;
    gap: 4px;
    width: auto;
    min-width: 60px;
  }

  .left-nav-btn .nav-icon {
    font-size: 22px;
    min-width: auto;
  }
  
  .left-nav-btn .nav-svg {
    width: 22px;
    height: 22px;
  }

  .left-nav-btn .nav-text {
    font-size: 10px;
    text-align: center;
  }

  .nav-bottom-group {
    flex-direction: row;
    margin-top: 0;
    margin-left: 10px;
  }

  .left-action-btn {
    height: 40px;
    padding: 0 15px;
    font-size: 14px;
    min-width: 80px;
  }

  .main-content {
    margin-left: 0;
    max-width: 100vw;
    padding: 25px 20px;
    padding-bottom: 90px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }

  .new-post-btn {
    align-self: flex-start;
  }

  .waterfall-grid {
    column-count: 2;
  }

  .status-filter-tabs {
    justify-content: center;
  }
}

@media (min-width: 769px) and (max-width: 1024px) {
  .left-nav {
    width: 300px;
  }

  .main-content {
    margin-left: 300px;
    max-width: calc(100vw - 300px);
  }

  .waterfall-grid {
    column-count: 3;
  }
}
</style>