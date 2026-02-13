<template>
  <div class="home-page">
    <!-- 纯色背景 -->
    <div class="background-container">
      <!-- 背景层 -->
      <div class="solid-background"></div>
    </div>

    <!-- 整体布局：左侧导航 + 右侧主内容 -->
    <div class="layout-container">
      <!-- 左侧导航栏组件 -->
    <Navigation 
      subtitle="欢迎回来^_^"
      active-nav="发现"
      :custom-content="true"
      @logout="handleLogout"
    >
      <template #custom-content>
        <div class="notice-content">
          <div class="notice-title">📢 毕业季失物招领专场</div>
          <div class="notice-desc">别问，问就是捡到的～ 毕业季专属失物找回通道已开启！</div>
        </div>
        <div class="notice-time">2024-06-15</div>
      </template>
    </Navigation>

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

             <!-- 校区筛选 -->
            <div class="filter-group">
              <div class="group-title">校区</div>
              <div class="option-buttons">
                <button 
                  v-for="campus in campuses" 
                  :key="campus.value"
                  class="option-btn"
                  :class="{ active: filterParams.campus === campus.value }"
                  @click="toggleFilter('campus', campus.value)"
                >
                  {{ campus.label }}
                </button>
              </div>
            </div>

           <!-- 物品分类筛选 -->
          <div class="filter-group">
            <div class="group-title">物品分类</div>
            
            <!-- 一级分类 -->
            <div v-if="categoryTree.length > 0" class="category-level">
              <div class="option-buttons">
                <button 
                  class="option-btn" 
                  :class="{ active: filterParams.category === '' }" 
                  @click="toggleCategoryFilter('', '')" 
                >
                  不限
                </button>
                <button 
                  v-for="category in categoryTree" 
                  :key="category.id" 
                  class="option-btn" 
                  :class="{ active: filterParams.category === category.id.toString() }" 
                  @click="toggleCategoryFilter(category.id.toString(), '')" 
                >
                  {{ category.name }}
                </button>
              </div>
            </div>
            
            <!-- 二级分类 -->
            <div v-if="filterParams.category && getSubCategories(filterParams.category).length > 0" class="category-level sub-category">
              <!-- <div class="group-title sub-title">{{ getCategoryName(filterParams.category) }}</div> -->
              <div class="option-buttons">
                <button 
                  class="option-btn" 
                  :class="{ active: filterParams.subCategory === '' }" 
                  @click="toggleSubCategoryFilter('')" 
                >
                  不限
                </button>
                <button 
                  v-for="subCategory in getSubCategories(filterParams.category)" 
                  :key="subCategory.id" 
                  class="option-btn" 
                  :class="{ active: filterParams.subCategory === subCategory.id.toString() }" 
                  @click="toggleSubCategoryFilter(subCategory.id.toString())" 
                >
                  {{ subCategory.name }}
                </button>
              </div>
            </div>
            
            <!-- 加载状态 -->
            <div v-else-if="categoryTree.length === 0" class="loading-text">
              加载分类中...
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
            <button 
              class="filter-tab" 
              :class="{ active: currentFilter === 'all' }"
              @click="setFilter('all')"
            >
              全部
            </button>
            <button 
              class="filter-tab" 
              :class="{ active: currentFilter === 'lost' }"
              @click="setFilter('lost')"
            >
              失物
            </button>
            <button 
              class="filter-tab" 
              :class="{ active: currentFilter === 'found' }"
              @click="setFilter('found')"
            >
              招领
            </button>
          </div>
        </section>

        <!-- ✅ 瀑布流容器（真正 masonry） -->
        <div class="waterfall-grid">
          <!-- 失物 -->
          <div
            v-for="item in filteredLostItems"
            :key="`lost-${item.itemId}`"
            class="waterfall-card lost-card"
            @click="goDetail(item.itemId)"
          >
            <img
              class="card-image"
              :src="item.firstImageUrl || '/home/默认.jpg'"
            />
            <div class="card-tag lost-tag">失物</div>

            <div class="card-content">
              <div class="card-name">{{ item.name }}</div>
              <div class="card-info">
                <span class="info-item campus">🏫 {{ getCampusName(item.locationId) }}</span>
                <span class="info-item">📍 {{ item.locationName }}</span>
              </div>
              <div class="card-footer">
                <button class="detail-btn">查看详情</button>
              </div>
            </div>
          </div>

          <!-- 招领 -->
          <div
            v-for="item in filteredFoundItems"
            :key="`found-${item.itemId}`"
            class="waterfall-card found-card"
            @click="goDetail(item.itemId)"
          >
            <img
              class="card-image"
              :src="item.firstImageUrl || '/home/默认.jpg'"
            />
            <div class="card-tag found-tag">招领</div>

            <div class="card-content">
              <div class="card-name">{{ item.name }}</div>
              <div class="card-info">
                <span class="info-item campus">🏫 {{ getCampusName(item.locationId) }}</span>
                <span class="info-item">📍 {{ item.locationName }}</span>
              </div>
              <div class="card-footer">
                <button class="detail-btn">查看详情</button>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>

    <ItemDetailView
      :visible="showItemDetail"
      :itemId="currentItemId"
      @close="handleDetailClose"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import ItemDetailView from './ItemDetailView.vue'
import Navigation from './navigation.vue'

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

/* ================= 物品数据 ================= */
const allItems = ref<any[]>([]) // 所有物品数据
const currentFilter = ref('all')
const searchKeyword = ref('')

/* ================= 分类数据（从接口获取） ================= */
const categoryTree = ref<any[]>([]) // 完整的分类树
const subCategoriesMap = ref<Record<number, any[]>>({}) // 二级分类映射表

/* ================= 筛选功能 ================= */
const showFilterPanel = ref(false)
const filterParams = ref({
  itemType: '',
  category: '',
  subCategory: '',
  campus: '',
  timeRange: '',
  status: ''
})

// 筛选选项数据
const itemTypes = [
  { value: '', label: '不限' },
  { value: '1', label: '失物' },
  { value: '2', label: '招领' }
]

const campuses = [
  { value: '', label: '不限' },
  { value: '1', label: '朝晖校区' },
  { value: '2', label: '屏峰校区' },
  { value: '3', label: '莫干山校区' }
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

/* ================= 计算属性：过滤后的物品列表 ================= */
const filteredLostItems = computed(() => {
  let items = allItems.value.filter(item => item.itemCategory === 1)
  
  // 应用搜索关键词
  if (searchKeyword.value.trim()) {
    const keyword = searchKeyword.value.toLowerCase().trim()
    items = items.filter(item => 
      item.name?.toLowerCase().includes(keyword) ||
      item.locationName?.toLowerCase().includes(keyword)
    )
  }
  
  // 应用筛选条件
  if (filterParams.value.itemType) {
    items = items.filter(item => item.itemCategory === parseInt(filterParams.value.itemType))
  }
  
  // 分类筛选
  if (filterParams.value.category) {
    if (filterParams.value.subCategory) {
      // 二级分类筛选
      items = items.filter(item => 
        item.itemType === parseInt(filterParams.value.subCategory)
      )
    } else {
      // 一级分类筛选：获取该一级分类下的所有二级分类ID
      const subCategoryIds = getSubCategories(filterParams.value.category).map(sub => sub.id)
      if (subCategoryIds.length > 0) {
        items = items.filter(item => 
          subCategoryIds.includes(item.itemType)
        )
      }
    }
  }
  
  if (filterParams.value.campus) {
    items = items.filter(item => {
      if (!item.locationId) return false
      const campusCode = Math.floor(item.locationId / 10000)
      return campusCode === parseInt(filterParams.value.campus)
    })
  }
  
  // 时间范围筛选
  if (filterParams.value.timeRange) {
    const now = new Date()
    items = items.filter(item => {
      if (!item.happenTime) return false
      const happenTime = new Date(item.happenTime)
      
      switch (filterParams.value.timeRange) {
        case 'today':
          return happenTime.toDateString() === now.toDateString()
        case 'week':
          const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
          return happenTime >= weekAgo
        case 'month':
          const monthAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000)
          return happenTime >= monthAgo
        case '3month':
          const threeMonthsAgo = new Date(now.getTime() - 90 * 24 * 60 * 60 * 1000)
          return happenTime >= threeMonthsAgo
        default:
          return true
      }
    })
  }
  
  // 根据当前筛选器类型过滤
  if (currentFilter.value === 'lost') {
    return items
  } else if (currentFilter.value === 'found') {
    return []
  } else {
    return items
  }
})

const filteredFoundItems = computed(() => {
  let items = allItems.value.filter(item => item.itemCategory === 2)
  
  // 应用搜索关键词
  if (searchKeyword.value.trim()) {
    const keyword = searchKeyword.value.toLowerCase().trim()
    items = items.filter(item => 
      item.name?.toLowerCase().includes(keyword) ||
      item.locationName?.toLowerCase().includes(keyword)
    )
  }
  
  // 应用筛选条件
  if (filterParams.value.itemType) {
    items = items.filter(item => item.itemCategory === parseInt(filterParams.value.itemType))
  }
  
  // 分类筛选
  if (filterParams.value.category) {
    if (filterParams.value.subCategory) {
      // 二级分类筛选
      items = items.filter(item => 
        item.itemType === parseInt(filterParams.value.subCategory)
      )
    } else {
      // 一级分类筛选：获取该一级分类下的所有二级分类ID
      const subCategoryIds = getSubCategories(filterParams.value.category).map(sub => sub.id)
      if (subCategoryIds.length > 0) {
        items = items.filter(item => 
          subCategoryIds.includes(item.itemType)
        )
      }
    }
  }
  
  if (filterParams.value.campus) {
    items = items.filter(item => {
      if (!item.locationId) return false
      const campusCode = Math.floor(item.locationId / 10000)
      return campusCode === parseInt(filterParams.value.campus)
    })
  }
  
  // 时间范围筛选
  if (filterParams.value.timeRange) {
    const now = new Date()
    items = items.filter(item => {
      if (!item.happenTime) return false
      const happenTime = new Date(item.happenTime)
      
      switch (filterParams.value.timeRange) {
        case 'today':
          return happenTime.toDateString() === now.toDateString()
        case 'week':
          const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
          return happenTime >= weekAgo
        case 'month':
          const monthAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000)
          return happenTime >= monthAgo
        case '3month':
          const threeMonthsAgo = new Date(now.getTime() - 90 * 24 * 60 * 60 * 1000)
          return happenTime >= threeMonthsAgo
        default:
          return true
      }
    })
  }
  
  // 根据当前筛选器类型过滤
  if (currentFilter.value === 'found') {
    return items
  } else if (currentFilter.value === 'lost') {
    return []
  } else {
    return items
  }
})

/* ================= 校区信息 ================= */
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

/* ================= 筛选功能方法 ================= */
const toggleFilterPanel = () => {
  showFilterPanel.value = !showFilterPanel.value
}

const toggleFilter = (type: string, value: string) => {
  if (filterParams.value[type as keyof typeof filterParams.value] === value) {
    filterParams.value[type as keyof typeof filterParams.value] = ''
  } else {
    filterParams.value[type as keyof typeof filterParams.value] = value
  }
}

// 分类筛选方法
const toggleCategoryFilter = (category: string, subCategory: string) => {
  filterParams.value.category = category
  filterParams.value.subCategory = subCategory
}

const toggleSubCategoryFilter = (subCategory: string) => {
  filterParams.value.subCategory = subCategory
}

// 获取子分类
const getSubCategories = (categoryId: string) => {
  const id = parseInt(categoryId)
  return subCategoriesMap.value[id] || []
}

// 获取分类名称
const getCategoryName = (categoryId: string) => {
  const id = parseInt(categoryId)
  // 在一级分类中查找
  const category = categoryTree.value.find(cat => cat.id === id)
  if (category) return category.name
  
  // 如果在二级分类中，找到其父分类
  for (const cat of categoryTree.value) {
    if (cat.children) {
      const subCategory = cat.children.find((sub: any) => sub.id === id)
      if (subCategory) {
        return cat.name // 返回父分类名称
      }
    }
  }
  
  return '物品类型'
}

const resetFilters = () => {
  filterParams.value = {
    itemType: '',
    category: '',
    subCategory: '',
    campus: '',
    timeRange: '',
    status: ''
  }
  searchKeyword.value = ''
}

/* ================= 搜索处理 ================= */
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



/* ================= 物品详情卡片 ================= */
const showItemDetail = ref(false)
const currentItemId = ref<number | null>(null)

/* ================= 生命周期 ================= */
onMounted(() => {
  loadUser()
  loadCategoryTree() // 先加载分类树
  loadItems()
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

// 退出登录处理
const handleLogout = async () => {
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
    router.push('/login')
  }
}

// 加载分类树数据
async function loadCategoryTree() {
  try {
    const res = await axios.get('/api/item/category/tree')
    console.log('分类树接口返回:', res.data)
    
    if (res.data.code === 200) {
      const treeData = res.data.data
      categoryTree.value = treeData
      
      // 构建子分类映射表
      const map: Record<number, any[]> = {}
      treeData.forEach((category: any) => {
        if (category.children && category.children.length > 0) {
          map[category.id] = category.children
        }
      })
      subCategoriesMap.value = map
      
      console.log('分类树加载成功:', categoryTree.value)
      console.log('子分类映射:', subCategoriesMap.value)
    }
  } catch (error) {
    console.error('加载分类树失败:', error)
    // 使用默认数据作为后备
    const defaultTree = [
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
    
    categoryTree.value = defaultTree
    
    // 构建子分类映射表
    const map: Record<number, any[]> = {}
    defaultTree.forEach((category: any) => {
      if (category.children && category.children.length > 0) {
        map[category.id] = category.children
      }
    })
    subCategoriesMap.value = map
  }
}

async function loadItems() {
  try {
    const res = await axios.get('/api/item/list')
    console.log('物品列表接口返回:', res.data)
    
    if (res.data.code === 200) {
      const list = res.data.data.list
      allItems.value = list
      
      console.log('失物数量:', list.filter((i: any) => i.itemCategory === 1).length)
      console.log('招领数量:', list.filter((i: any) => i.itemCategory === 2).length)
      console.log('所有物品:', list)
    }
  } catch (error) {
    console.error('加载物品列表失败:', error)
    // 模拟数据用于演示
    const mockData = [
      { 
        itemId: 1, 
        name: '校园卡（张三）', 
        locationName: '图书馆三楼自习区', 
        locationId: 10301,
        itemCategory: 1,
        itemType: 101,
        happenTime: '2025-03-01 14:00:00',
        rewardAmount: 50,
        feature: '内有学生证和身份证'
      },
      { 
        itemId: 2, 
        name: '黑色雨伞', 
        locationName: '教学楼A栋门口', 
        itemCategory: 1,
        itemType: 301,
        happenTime: '2025-03-01 10:30:00',
        rewardAmount: 20,
        feature: '长柄黑色雨伞'
      },
      { 
        itemId: 3, 
        name: 'AirPods耳机', 
        locationName: '运动场看台', 
        itemCategory: 1,
        itemType: 201,
        happenTime: '2025-03-02 09:15:00',
        rewardAmount: 100,
        feature: '白色，右耳有划痕'
      },
      { 
        itemId: 4, 
        name: '水杯（蓝色）', 
        locationName: '食堂二楼', 
        itemCategory: 1,
        itemType: 301,
        happenTime: '2025-03-02 12:00:00',
        rewardAmount: 0,
        feature: '蓝色保温杯'
      },
      { 
        itemId: 5, 
        name: '钥匙串', 
        locationName: '宿舍楼下', 
        itemCategory: 2,
        itemType: 304,
        happenTime: '2025-03-01 16:45:00',
        rewardAmount: 0,
        feature: '3把钥匙，1个U盘'
      },
      { 
        itemId: 6, 
        name: '笔记本', 
        locationName: '实验室302', 
        itemCategory: 2,
        itemType: 402,
        happenTime: '2025-03-01 14:20:00',
        rewardAmount: 0,
        feature: '黑色笔记本，内有笔记'
      },
      { 
        itemId: 7, 
        name: '校园卡（李四）', 
        locationName: '校门口保安室', 
        itemCategory: 2,
        itemType: 101,
        happenTime: '2025-03-02 08:30:00',
        rewardAmount: 50,
        feature: '学号2023123457'
      },
      { 
        itemId: 8, 
        name: '背包', 
        locationName: '篮球场', 
        itemCategory: 2,
        itemType: 501,
        happenTime: '2025-03-02 15:00:00',
        rewardAmount: 100,
        feature: '黑色双肩包'
      }
    ]
    
    allItems.value = mockData
  }
}

/* ================= 路由跳转和操作 ================= */
function goDetail(id: number) {
  currentItemId.value = id
  showItemDetail.value = true
}

function handleDetailClose() {
  showItemDetail.value = false
  currentItemId.value = null
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

function setFilter(filter: 'all' | 'lost' | 'found') {
  currentFilter.value = filter
}


</script>

<style scoped>
/* 基础布局 */
.home-page {
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
  /* background: #E3D2A1; */
  background: #f8f3d4;
  pointer-events: none;
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
  background: transparent;
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
  /* background: rgba(255, 255, 255, 0.15); */
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

/* 导航组件中的公告栏样式 */
.left-notice-card .notice-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.left-notice-card .notice-title {
  font-family: "Comic Sans MS", cursive;
  font-size: 16px;
  font-weight: 600;
  color: #a67c52;
}

.left-notice-card .notice-desc {
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: rgba(166, 124, 82, 0.8);
  line-height: 1.4;
  text-align: center;
  margin-bottom: 20px;
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding-right: 5px;
  word-wrap: break-word;
}

.left-notice-card .notice-time {
  font-family: "Comic Sans MS", cursive;
  font-size: 12px;
  color: rgba(166, 124, 82, 0.6);
  text-align: right;
  flex-shrink: 0;
  margin-top: 10px;
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
  width: 75%;
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
  border: 1.6px solid rgba(166, 124, 82, 0.4);
  font-size: 17.6px;
  outline: none;
  background: rgba(255, 255, 255, 0.35);
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
  background: rgba(255, 255, 255, 0.45);
  backdrop-filter: blur(15px);
  box-shadow: 0 0 0 3px rgba(243, 129, 129, 0.15);
}

/* 筛选按钮 */
.filter-btn {
  display: flex;
  align-items: center;
  gap: 6.4px;
  padding: 9.6px 16px;
  border: 1.6px solid rgba(166, 124, 82, 0.4);
  border-radius: 22.4px;
  background: rgba(255, 255, 255, 0.35);
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
  border-color: #f37f75;
  background: #f37f75;
  color: white;
}

/* 分类筛选样式 */
.category-level {
  margin-bottom: 12px;
}

.category-level.sub-category {
  margin-left: 20px;
  padding-left: 12px;
  border-left: 2px solid #f0f0f0;
}

.sub-title {
  font-size: 16px !important;
  color: #666 !important;
  margin-bottom: 8px !important;
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
  border-color: #f37f75;
  background: #f37f75;
  color: white;
  font-size: 16px;
}

.collapse-btn:hover {
  background: #e62e47;
}

/* 筛选标签栏 */
.filter-section {
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(15px);
  border-radius: 20px;
  padding: 20px 25px;
  border: 2px solid rgba(166, 124, 82, 0.2);
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
}

.waterfall-card:hover {
  transform: translateY(-6px);
}

/* 物品卡片样式 */
.card-image-container {
  position: relative;
  height: 200px;
  overflow: hidden;
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
  font-size: 16px;
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
    .waterfall-grid {
    column-count: 2;
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

  /* 移动端隐藏导航组件中的公告栏 */
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


  .filter-tabs {
    justify-content: center;
  }
}

/* 平板端适配（769px-1024px） */
@media (min-width: 769px) and (max-width: 1024px) {
  .waterfall-grid {
    column-count: 3;
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