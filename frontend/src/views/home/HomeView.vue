<template>
  <div class="home-page">
    <!-- 背景图片 -->
    <div class="background-container">
      <img 
        src="/login/login_background.png" 
        alt="首页背景" 
        class="background-image background-loaded"
      />
      <!-- 毛玻璃背景层 -->
      <div class="glass-layer-full glass-layer-visible"></div>
    </div>

    <!-- 整体布局：左侧导航 + 右侧主内容 -->
    <div class="layout-container">
      <!-- 左侧导航栏 -->
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
              :class="{ active: nav.active }"
              @click="nav.handler"
            >
              <span class="nav-icon">
                <img :src="nav.icon" :alt="nav.name" class="nav-svg" />
              </span>
              <span class="nav-text">{{ nav.name }}</span>
            </button>
        </div>

        <!-- 左侧中间：公告栏 -->
        <div class="left-notice-card bubble">
          <div class="notice-content">
            <div class="notice-title">📢 毕业季失物招领专场</div>
            <div class="notice-desc">别问，问就是捡到的～ 毕业季专属失物找回通道已开启！</div>
          </div>
          <div class="notice-time">2024-06-15</div>
        </div>

        <!-- 左侧下半区：操作按钮 -->
        <div class="nav-bottom-group">
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
        <!-- 搜索和筛选区域 -->
        <section class="search-filter-section">
          <div class="search-container">
            <div class="search-input-group">
              <span class="search-icon">
                <img src="/home/搜索.svg" alt="搜索" class="search-svg" />
              </span>
              <input
                v-model="searchKeyword"
                type="text"
                placeholder="搜索失物或招领物品..."
                class="search-input"
                @input="handleSearch"
              />
            </div>
            
            <!-- 筛选按钮（居右） -->
            <div class="filter-btn-container">
              <button 
                class="filter-btn"
                :class="{ active: showFilterPanel }"
                @click="toggleFilterPanel"
              >
                <span class="filter-text">筛选</span>
                <span class="filter-arrow" :class="{ rotated: showFilterPanel }">▼</span>
              </button>
            </div>
          </div>

          <!-- 筛选面板 -->
          <div v-if="showFilterPanel" class="filter-panel">
            <div class="panel-header">
              <h3 class="panel-title">筛选</h3>
            </div>
            
            <!-- 物品类型筛选 -->
            <div class="filter-group">
              <div class="group-title">物品类型</div>
              <div class="option-buttons">
                <button 
                  v-for="type in itemTypes" 
                  :key="type.value"
                  class="option-btn"
                  :class="{ active: filterParams.itemType === type.value }"
                  @click="toggleFilter('itemType', type.value)"
                >
                  {{ type.label }}
                </button>
              </div>
            </div>

            <!-- 地点筛选 -->
            <div class="filter-group">
              <div class="group-title">地点</div>
              <div class="option-buttons">
                <button 
                  v-for="location in locations" 
                  :key="location.value"
                  class="option-btn"
                  :class="{ active: filterParams.location === location.value }"
                  @click="toggleFilter('location', location.value)"
                >
                  {{ location.label }}
                </button>
              </div>
            </div>

            <!-- 时间范围筛选 -->
            <div class="filter-group">
              <div class="group-title">时间范围</div>
              <div class="option-buttons">
                <button 
                  v-for="timeRange in timeRanges" 
                  :key="timeRange.value"
                  class="option-btn"
                  :class="{ active: filterParams.timeRange === timeRange.value }"
                  @click="toggleFilter('timeRange', timeRange.value)"
                >
                  {{ timeRange.label }}
                </button>
              </div>
            </div>

            <!-- 物品状态筛选 -->
            <div class="filter-group">
              <div class="group-title">物品状态</div>
              <div class="option-buttons">
                <button 
                  v-for="status in itemStatuses" 
                  :key="status.value"
                  class="option-btn"
                  :class="{ active: filterParams.status === status.value }"
                  @click="toggleFilter('status', status.value)"
                >
                  {{ status.label }}
                </button>
              </div>
            </div>

            <!-- 底部操作区 -->
            <div class="panel-footer">
              <div class="footer-divider"></div>
              <div class="footer-buttons">
                <button class="reset-btn" @click="resetFilters">重置</button>
                <button class="collapse-btn" @click="toggleFilterPanel">收起</button>
              </div>
            </div>
          </div>
        </section>

        <!-- 筛选标签栏 -->
        <section class="filter-section">
          <div class="filter-tabs">
            <button class="filter-tab active" @click="setFilter('all')">全部</button>
            <button class="filter-tab" @click="setFilter('lost')">失物</button>
            <button class="filter-tab" @click="setFilter('found')">招领</button>
          </div>
        </section>

        <!-- 瀑布流卡片容器 -->
        <div class="waterfall-grid">
          <!-- 失物卡片 -->
          <div
            v-for="item in filteredLostItems"
            :key="`lost-${item.itemId}`"
            class="waterfall-card item-card lost-card"
            @click="goDetail(item.itemId)"
          >
            <div class="card-image-container">
              <img class="card-image" src="/home/avatar.png" />
              <div class="card-tag lost-tag">失物</div>
            </div>
            <div class="card-content">
              <div class="card-name">{{ item.name }}</div>
              <div class="card-info">
                <span class="info-item">
                  <span class="info-icon">📍</span>
                  {{ item.locationName }}
                </span>
                <span class="info-item">
                  <span class="info-icon">🕒</span>
                  2小时前
                </span>
              </div>
              <div class="card-footer">
                <button class="detail-btn" @click.stop="goDetail(item.itemId)">查看详情</button>
              </div>
            </div>
          </div>

          <!-- 招领卡片 -->
          <div
            v-for="item in filteredFoundItems"
            :key="`found-${item.itemId}`"
            class="waterfall-card item-card found-card"
            @click="goDetail(item.itemId)"
          >
            <div class="card-image-container">
              <img class="card-image" src="/home/avatar.png" />
              <div class="card-tag found-tag">招领</div>
            </div>
            <div class="card-content">
              <div class="card-name">{{ item.name }}</div>
              <div class="card-info">
                <span class="info-item">
                  <span class="info-icon">📍</span>
                  {{ item.locationName }}
                </span>
                <span class="info-item">
                  <span class="info-icon">🕒</span>
                  1天前
                </span>
              </div>
              <div class="card-footer">
                <button class="detail-btn" @click.stop="goDetail(item.itemId)">查看详情</button>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

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

/* ================= 物品推荐 ================= */
const lostItems = ref<any[]>([])
const foundItems = ref<any[]>([])
const currentFilter = ref('all')
const searchKeyword = ref('')
const originalLostItems = ref<any[]>([])
const originalFoundItems = ref<any[]>([])
const allItems = ref<any[]>([]) // 所有物品数据

/* ================= 筛选功能 ================= */
const showFilterPanel = ref(false)
const filterParams = ref({
  itemType: '',
  location: '',
  timeRange: '',
  status: ''
})

// 筛选选项数据
const itemTypes = [
  { value: '', label: '不限' },
  { value: '1', label: '失物' },
  { value: '2', label: '招领' }
]

const locations = [
  { value: '', label: '不限' },
  { value: '图书馆', label: '图书馆' },
  { value: '教学楼', label: '教学楼' },
  { value: '宿舍楼', label: '宿舍楼' },
  { value: '食堂', label: '食堂' },
  { value: '运动场', label: '运动场' },
  { value: '实验室', label: '实验室' },
  { value: '校门口', label: '校门口' }
]

const timeRanges = [
  { value: '', label: '不限' },
  { value: 'today', label: '今天' },
  { value: 'week', label: '本周' },
  { value: 'month', label: '本月' },
  { value: '3month', label: '近3个月' }
]

const itemStatuses = [
  { value: '', label: '不限' },
  { value: '1', label: '待审核' },
  { value: '2', label: '已审核' },
  { value: '3', label: '已完成' }
]

// 计算属性：过滤后的物品列表
const filteredLostItems = computed(() => {
  let items = [...allItems.value].filter(item => item.itemType === 1)
  
  // 应用搜索关键词
  if (searchKeyword.value.trim()) {
    const keyword = searchKeyword.value.toLowerCase().trim()
    items = items.filter(item => 
      item.name?.toLowerCase().includes(keyword) ||
      item.locationName?.toLowerCase().includes(keyword) ||
      item.feature?.toLowerCase().includes(keyword)
    )
  }
  
  // 应用筛选条件
  if (filterParams.value.itemType) {
    items = items.filter(item => item.itemType === parseInt(filterParams.value.itemType))
  }
  
  if (filterParams.value.location) {
    items = items.filter(item => item.locationName?.includes(filterParams.value.location))
  }
  
  // 根据当前筛选器类型过滤
  if (currentFilter.value === 'lost') {
    return items.slice(0, 8)
  } else if (currentFilter.value === 'found') {
    return []
  } else {
    return items.slice(0, 8)
  }
})

const filteredFoundItems = computed(() => {
  let items = [...allItems.value].filter(item => item.itemType === 2)
  
  // 应用搜索关键词
  if (searchKeyword.value.trim()) {
    const keyword = searchKeyword.value.toLowerCase().trim()
    items = items.filter(item => 
      item.name?.toLowerCase().includes(keyword) ||
      item.locationName?.toLowerCase().includes(keyword) ||
      item.feature?.toLowerCase().includes(keyword)
    )
  }
  
  // 应用筛选条件
  if (filterParams.value.itemType) {
    items = items.filter(item => item.itemType === parseInt(filterParams.value.itemType))
  }
  
  if (filterParams.value.location) {
    items = items.filter(item => item.locationName?.includes(filterParams.value.location))
  }
  
  // 根据当前筛选器类型过滤
  if (currentFilter.value === 'found') {
    return items.slice(0, 8)
  } else if (currentFilter.value === 'lost') {
    return []
  } else {
    return items.slice(0, 8)
  }
})

/** 筛选面板切换 */
const toggleFilterPanel = () => {
  showFilterPanel.value = !showFilterPanel.value
}

/** 筛选条件切换 */
const toggleFilter = (type: string, value: string) => {
  if (filterParams.value[type as keyof typeof filterParams.value] === value) {
    filterParams.value[type as keyof typeof filterParams.value] = ''
  } else {
    filterParams.value[type as keyof typeof filterParams.value] = value
  }
}

/** 重置筛选 */
const resetFilters = () => {
  filterParams.value = {
    itemType: '',
    location: '',
    timeRange: '',
    status: ''
  }
  searchKeyword.value = ''
}

/** 搜索处理 - 使用防抖优化 */
let searchTimer: any = null
const handleSearch = () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    // 计算属性会自动响应搜索关键词变化，无需额外处理
  }, 300)
}

// 监听筛选参数变化
watch(filterParams, () => {
  // 筛选参数变化时，计算属性会自动重新计算
}, { deep: true })

/* ================= 左侧上半区核心导航 ================= */
const navItems = reactive([
  {
    name: '发现',
    icon: '/home/发现.svg',
    active: true,
    handler: () => {}
  },
  {
    name: '发布',
    icon: '/home/发布.svg',
    active: false,
    handler: goPublish
  },
  {
    name: '消息',
    icon: '/home/消息.svg',
    active: false,
    handler: goMessages
  },
  {
    name: '我的',
    icon: '/home/我的.svg',
    active: false,
    handler: goMyPosts
  },
  {
    name: '设置',
    icon: '/home/设置.svg',
    active: false,
    handler: goSettings
  }
])

onMounted(() => {
  loadUser()
  loadItems()
})

async function loadUser() {
  try {
    const res = await axios.get('/api/user/info')
    if (res.data.code === 0) {
      user.value = res.data.data
    }
  } catch (error) {
    console.error('加载用户信息失败:', error)
    // 模拟数据用于演示
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

async function loadItems() {
  try {
    const res = await axios.get('/api/item/list')
    if (res.data.code === 200) {
      const list = res.data.data.list
      allItems.value = list
      
      // 初始化失物和招领列表
      lostItems.value = list.filter((i: any) => i.itemType === 1).slice(0, 8)
      foundItems.value = list.filter((i: any) => i.itemType === 2).slice(0, 8)
      originalLostItems.value = [...lostItems.value]
      originalFoundItems.value = [...foundItems.value]
    }
  } catch (error) {
    console.error('加载物品列表失败:', error)
    // 模拟数据用于演示
    const mockData = [
      { 
        itemId: 1, 
        name: '校园卡（张三）', 
        locationName: '图书馆三楼自习区', 
        itemType: 1,
        itemCategory: 1,
        happenTime: '2025-03-01 14:00:00',
        rewardAmount: 50,
        feature: '内有学生证和身份证'
      },
      { 
        itemId: 2, 
        name: '黑色雨伞', 
        locationName: '教学楼A栋门口', 
        itemType: 1,
        itemCategory: 2,
        happenTime: '2025-03-01 10:30:00',
        rewardAmount: 20,
        feature: '长柄黑色雨伞'
      },
      { 
        itemId: 3, 
        name: 'AirPods耳机', 
        locationName: '运动场看台', 
        itemType: 1,
        itemCategory: 3,
        happenTime: '2025-03-02 09:15:00',
        rewardAmount: 100,
        feature: '白色，右耳有划痕'
      },
      { 
        itemId: 4, 
        name: '水杯（蓝色）', 
        locationName: '食堂二楼', 
        itemType: 1,
        itemCategory: 4,
        happenTime: '2025-03-02 12:00:00',
        rewardAmount: 0,
        feature: '蓝色保温杯'
      },
      { 
        itemId: 5, 
        name: '钥匙串', 
        locationName: '宿舍楼下', 
        itemType: 2,
        itemCategory: 5,
        happenTime: '2025-03-01 16:45:00',
        rewardAmount: 0,
        feature: '3把钥匙，1个U盘'
      },
      { 
        itemId: 6, 
        name: '笔记本', 
        locationName: '实验室302', 
        itemType: 2,
        itemCategory: 6,
        happenTime: '2025-03-01 14:20:00',
        rewardAmount: 0,
        feature: '黑色笔记本，内有笔记'
      },
      { 
        itemId: 7, 
        name: '校园卡（李四）', 
        locationName: '校门口保安室', 
        itemType: 2,
        itemCategory: 1,
        happenTime: '2025-03-02 08:30:00',
        rewardAmount: 50,
        feature: '学号2023123457'
      },
      { 
        itemId: 8, 
        name: '背包', 
        locationName: '篮球场', 
        itemType: 2,
        itemCategory: 7,
        happenTime: '2025-03-02 15:00:00',
        rewardAmount: 100,
        feature: '黑色双肩包'
      }
    ]
    
    allItems.value = mockData
    lostItems.value = mockData.filter(item => item.itemType === 1)
    foundItems.value = mockData.filter(item => item.itemType === 2)
    originalLostItems.value = [...lostItems.value]
    originalFoundItems.value = [...foundItems.value]
  }
}

/* ================= 路由跳转 ================= */
function goDetail(id: number) {
  router.push(`/item/detail?itemId=${id}`)
}

function goPublish() {
  router.push('/publish')
}

function goMyPosts() {
  router.push('/my-posts')
}

function goMessages() {
  router.push('/messages')
}

function goSettings() {
  router.push('/settings')
}

async function logout() {
  try {
    // 根据接口文档，退出登录需要调用接口
    const userId = user.value.id
    if (userId) {
      await axios.post('/api/user/logout', { userId })
    }
  } catch (error) {
    console.error('退出登录失败:', error)
  } finally {
    // 清除本地存储
    localStorage.clear()
    // 跳转到登录页
    router.push('/login')
  }
}

/* ================= 筛选切换 ================= */
function setFilter(filter: string) {
  currentFilter.value = filter
  
  // 更新标签激活状态
  const tabs = document.querySelectorAll('.filter-tab')
  tabs.forEach(tab => tab.classList.remove('active'))
  
  // 根据filter值设置对应的tab为active
  let activeIndex = 0
  switch(filter) {
    case 'all':
      activeIndex = 0
      break
    case 'lost':
      activeIndex = 1
      break
    case 'found':
      activeIndex = 2
      break
  }
  
  if (tabs[activeIndex]) {
    tabs[activeIndex].classList.add('active')
  }
}
</script>

<style scoped>
/* 基础布局 */
.home-page {
  width: 100vw;
  min-height: 100vh;
  position: relative;
  overflow: hidden;
  background: #fce38a;
}

/* 背景图片容器 */
.background-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
  overflow: hidden;
}

.background-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  opacity: 1;
  transform: scale(1);
}

/* 全屏毛玻璃层 */
.glass-layer-full {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.1);
  pointer-events: none;
  will-change: backdrop-filter;
}

/* 整体布局：左侧导航 + 右侧主内容 */
.layout-container {
  position: relative;
  z-index: 2;
  width: 100%;
  min-height: 100vh;
  display: flex;
}

/* 左侧导航栏：进一步拓宽宽度，垂直布局，上下分组+中间公告 */
.left-nav {
  width: 288px;
  height: 100vh;
  position: fixed;
  top: 0;
  left: 0;
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-right: 1.6px solid rgba(166, 124, 82, 0.2);
  /* 进一步增加内边距 */
  padding: 24px;
  display: flex;
  flex-direction: column;
  z-index: 10;
  /* 确保不会溢出 */
  box-sizing: border-box;
}

/* 左侧用户信息区域 */
.user-info-container {
  background: rgba(255, 255, 255, 0.3);
  backdrop-filter: blur(10px);
  border-radius: 12.8px;
  padding: 16px;
  border: 1.6px solid rgba(166, 124, 82, 0.15);
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

/* 左侧上半区：核心导航组 */
.nav-top-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 8px;
}

/* 左侧导航按钮样式（左右布局） */
.left-nav-btn {
  background: transparent;
  border: none;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 16px;
  cursor: pointer;
  padding: 14.4px 50px;
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
  background: rgba(243, 129, 129, 0.2);
  font-weight: 600;
}

.left-nav-btn:hover {
  background: rgba(255, 255, 255, 0.3);
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

/* 左侧中间：公告栏 */
.left-notice-card {
  background: rgba(255, 255, 255, 0.35);
  backdrop-filter: blur(10px);
  border-radius: 14.4px;
  padding: 16px;
  border: 1.6px solid rgba(166, 124, 82, 0.25);
  margin: 8px 0;
  display: flex;
  flex-direction: column;
  /* 高度自适应设置 */
  max-height: 300px; /* 限制最大高度 */
  min-height: 96px; /* 确保最小高度 */
  /* 滚动设置 */
  overflow-y: auto; /* 启用滚动 */
  scrollbar-width: thin;
  scrollbar-color: rgba(166, 124, 82, 0.15) transparent;
  /* 确保内部元素布局正确 */
  box-sizing: border-box;
}

/* 内部元素 */
.left-notice-card .notice-title {
  font-family: "Comic Sans MS", cursive;
  font-size: 18px;
  color: #a67c52;
  margin-bottom: 15px;
  font-weight: 600;
  text-align: center;
  flex-shrink: 0; /* 标题不压缩 */
}

.left-notice-card .notice-desc {
  font-family: "Comic Sans MS", cursive;
  font-size: 16px;
  color: rgba(166, 124, 82, 0.8);
  line-height: 1.5;
  text-align: center;
  margin-bottom: 20px;
  flex: 1; /* 占据剩余空间 */
  min-height: 0; /* 关键：允许内容区域滚动 */
  overflow-y: auto; /* 描述区域可以滚动 */
  padding-right: 5px; /* 给滚动条留空间 */
  word-wrap: break-word; /* 确保长文本换行 */
}

.left-notice-card .notice-time {
  font-family: "Comic Sans MS", cursive;
  font-size: 12px;
  color: rgba(166, 124, 82, 0.6);
  text-align: right;
  flex-shrink: 0; /* 时间不压缩 */
  margin-top: 10px; /* 与描述保持距离 */
}

/* 左侧下半区：操作按钮组 */
.nav-bottom-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: auto;
}

/* 左侧操作按钮样式 */
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



.logout-btn {
  background: linear-gradient(to right, #f38181, #f77d5f);
}

/* 右侧主内容区：自适应宽度，避开左侧导航 */
.main-content {
  flex: 1;
  min-height: 100vh;
  padding: 24px 28px;
  margin-left: 288px;
  max-width: calc(100vw - 288px);
  box-sizing: border-box;
}

/* 搜索和筛选区域 */
.search-filter-section {
  margin-bottom: 25px;
  position: relative;
}

.search-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 15px;
}

.filter-btn-container {
  display: flex;
  justify-content: flex-end;
  min-width: 120px;
}

.search-input-group {
  position: relative;
  width: 100%;
  max-width: 600px;
  flex: 1;
}

.search-icon {
  position: absolute;
  left: 20px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 20px;
  color: rgba(166, 124, 82, 0.7);
  z-index: 2;
  display: flex;
  align-items: center;
  justify-content: center;
}

.search-svg {
  width: 20px;
  height: 20px;
  object-fit: contain;
  filter: brightness(0.8);
}

.search-input {
  width: 100%;
  height: 54.4px;
  padding: 0 24px 0 56px;
  border-radius: 27.2px;
  border: 1.6px solid rgba(166, 124, 82, 0.3);
  font-size: 17.6px;
  outline: none;
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  transition: all 0.3s ease;
  font-family: "Comic Sans MS", cursive;
  color: #a67c52;
  font-weight: 500;
}

.search-input::placeholder {
  color: rgba(166, 124, 82, 0.6);
}

.search-input:focus {
  border-color: rgba(243, 129, 129, 0.7);
  background: rgba(255, 255, 255, 0.35);
  backdrop-filter: blur(15px);
  box-shadow: 0 0 0 3px rgba(243, 129, 129, 0.15);
}

/* 筛选按钮 */
.filter-btn {
  display: flex;
  align-items: center;
  gap: 6.4px;
  padding: 9.6px 16px;
  border: 1.6px solid rgba(166, 124, 82, 0.3);
  border-radius: 22.4px;
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(10px);
  color: #a67c52;
  font-family: "Comic Sans MS", cursive;
  font-size: 12.8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.filter-btn:hover,
.filter-btn.active {
  border-color: rgba(243, 129, 129, 0.7);
  background: rgba(255, 255, 255, 0.35);
  box-shadow: 0 0 0 3px rgba(243, 129, 129, 0.15);
}

.filter-text {
  font-size: 18px;
}

.filter-arrow {
  font-size: 12px;
  transition: transform 0.3s ease;
}

.filter-arrow.rotated {
  transform: rotate(180deg);
}

/* 筛选面板 */
.filter-panel {
  position: absolute;
  top: 100%;
  right: 0;
  width: 85%;
  max-width: 500px;
  background: white;
  border-radius: 14px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
  margin-top: 8px;
  z-index: 100;
  overflow: hidden;
}

.panel-header {
  padding: 16px 20px 12px;
  border-bottom: 1px solid #f0f0f0;
}

.panel-title {
  font-family: "Comic Sans MS", cursive;
  font-size: 20px;
  color: #333;
  margin: 0;
  font-weight: 600;
}

.filter-group {
  padding: 16px 20px;
  border-bottom: 1px solid #f0f0f0;
}

.group-title {
  font-family: "Comic Sans MS", cursive;
  font-size: 18px;
  color: #333;
  margin-bottom: 11.2px;
  font-weight: 500;
}

.option-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.option-btn {
  padding: 11.2px 19.2px;
  border: 0.8px solid #e0e0e0;
  border-radius: 19.2px;
  background: #f8f8f8;
  color: #666;
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.option-btn:hover {
  border-color: #ccc;
  background: #f0f0f0;
}

.option-btn.active {
  border-color: #ff3852;
  background: #ff3852;
  color: white;
}

.panel-footer {
  padding: 12px 20px 16px;
}

.footer-divider {
  height: 1px;
  background: #f0f0f0;
  margin-bottom: 16px;
}

.footer-buttons {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.reset-btn,
.collapse-btn {
  flex: 1;
  padding: 14px 22px;
  border: 1px solid #e0e0e0;
  border-radius: 10px;
  background: white;
  color: #666;
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.reset-btn:hover {
  border-color: #ccc;
  background: #f8f8f8;
}

.collapse-btn {
  border-color: #ff3852;
  background: #ff3852;
  color: white;
  font-size: 16px;
}

.collapse-btn:hover {
  background: #e62e47;
}

/* 筛选标签栏 */
.filter-section {
  background: rgba(255, 255, 255, 0.18);
  backdrop-filter: blur(15px);
  border-radius: 20px;
  padding: 20px 25px;
  border: 2px solid rgba(166, 124, 82, 0.15);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
  margin-bottom: 25px;
}

.filter-tabs {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.filter-tab {
  padding: 12.8px 22.4px;
  border-radius: 19.2px;
  border: none;
  background: rgba(255, 255, 255, 0.3);
  color: #a67c52;
  font-family: "Comic Sans MS", cursive;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.filter-tab.active {
  background: linear-gradient(135deg, #f38181, #f77d5f);
  color: white;
  box-shadow: 0 4px 12px rgba(243, 129, 129, 0.3);
}

.filter-tab:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* 瀑布流网格 */
.waterfall-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 20px;
}

/* 瀑布流卡片基础样式 */
.waterfall-card {
  background: rgba(255, 255, 255, 0.35);
  backdrop-filter: blur(15px);
  border-radius: 16px;
  overflow: hidden;
  border: 1.6px solid rgba(166, 124, 82, 0.2);
  transition: all 0.3s ease;
  cursor: pointer;
  position: relative;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.waterfall-card:hover {
  transform: translateY(-5px);
  border-color: rgba(243, 129, 129, 0.5);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.15);
}

/* 物品卡片样式 */
.card-image-container {
  position: relative;
  height: 200px;
  overflow: hidden;
}

.card-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
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
}

.found-tag {
  background: linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%);
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
  font-size: 12.8px;
  color: rgba(166, 124, 82, 0.8);
}

.info-icon {
  font-size: 14.4px;
}

.card-footer {
  display: flex;
  justify-content: center;
  margin-top: 15px;
}

.detail-btn {
  padding: 9.6px 22.4px;
  border: none;
  border-radius: 11.2px;
  background: linear-gradient(to right, #f38181, #f77d5f);
  color: white;
  font-family: "Comic Sans MS", cursive;
  font-size: 12.8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(247, 125, 95, 0.3);
}

.detail-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(247, 125, 95, 0.4);
  background: linear-gradient(to right, #f77d5f, #f38181);
}

.detail-btn:active {
  transform: translateY(0);
}

/* 基础字体放大 */
body {
  font-size: 16px;
}

/* 响应式设计：移动端（768px以下） */
@media (max-width: 768px) {
  .layout-container {
    flex-direction: column;
  }

  /* 左侧导航移至底部，横向布局 */
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

  /* 移动端隐藏用户信息、公告栏 */
  .user-info-container,
  .left-notice-card {
    display: none;
  }

  /* 导航组调整为横向 */
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

  /* 底部操作按钮组 */
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



  /* 右侧主内容区 */
  .main-content {
    margin-left: 0;
    max-width: 100vw;
    padding: 25px 20px;
    padding-bottom: 90px; /* 给底部导航留空间 */
  }

  .waterfall-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }

  .filter-tabs {
    justify-content: center;
  }
}

/* 平板端适配（769px-1024px） */
@media (min-width: 769px) and (max-width: 1024px) {
  .waterfall-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .left-nav {
    width: 300px;
  }

  .main-content {
    margin-left: 300px;
    max-width: calc(100vw - 300px);
  }
  
  .user-nickname {
    max-width: 120px;
  }
}
</style>