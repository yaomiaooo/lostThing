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
            <div class="user-subtitle">欢迎回来</div>
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
            <span class="nav-icon">{{ nav.icon }}</span>
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
            <span class="btn-icon">🚪</span>
            <span class="btn-text">退出登录</span>
          </button>
        </div>
      </aside>

      <!-- 右侧主内容区域 -->
      <main class="main-content">
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
import { ref, onMounted, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()

/* ================= 用户信息 ================= */
const user = ref({
  realName: '加载中...'
})

/* ================= 物品推荐 ================= */
const lostItems = ref<any[]>([])
const foundItems = ref<any[]>([])
const currentFilter = ref('all')

const filteredLostItems = computed(() => {
  if (currentFilter.value === 'all' || currentFilter.value === 'lost') {
    return lostItems.value
  }
  return []
})

const filteredFoundItems = computed(() => {
  if (currentFilter.value === 'all' || currentFilter.value === 'found') {
    return foundItems.value
  }
  return []
})

/* ================= 左侧上半区核心导航 ================= */
const navItems = reactive([
  {
    name: '首页',
    icon: '🏠',
    active: true,
    handler: () => {}
  },
  {
    name: '发布',
    icon: '➕',
    active: false,
    handler: goPublish
  },
  {
    name: '我的',
    icon: '👤',
    active: false,
    handler: goMyPosts
  },
  {
    name: '消息',
    icon: '💌',
    active: false,
    handler: goMessages
  },
  {
    name: '设置',
    icon: '⚙️',
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
  }
}

async function loadItems() {
  try {
    const res = await axios.get('/api/item/list')
    if (res.data.code === 200) {
      const list = res.data.data.list
      lostItems.value = list.filter((i: any) => i.itemType === 1).slice(0, 4)
      foundItems.value = list.filter((i: any) => i.itemType === 2).slice(0, 4)
    }
  } catch (error) {
    console.error('加载物品列表失败:', error)
    // 模拟数据用于演示
    lostItems.value = [
      { itemId: 1, name: '校园卡（张三）', locationName: '图书馆三楼自习区', itemType: 1 },
      { itemId: 2, name: '黑色雨伞', locationName: '教学楼A栋门口', itemType: 1 },
      { itemId: 3, name: 'AirPods耳机', locationName: '运动场看台', itemType: 1 },
      { itemId: 4, name: '水杯（蓝色）', locationName: '食堂二楼', itemType: 1 }
    ]
    foundItems.value = [
      { itemId: 5, name: '钥匙串', locationName: '宿舍楼下', itemType: 2 },
      { itemId: 6, name: '笔记本', locationName: '实验室302', itemType: 2 },
      { itemId: 7, name: '校园卡（李四）', locationName: '校门口保安室', itemType: 2 },
      { itemId: 8, name: '背包', locationName: '篮球场', itemType: 2 }
    ]
  }
}

/* ================= 路由跳转 ================= */
function goDetail(id: number) {
  router.push(`/item/${id}`)
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

function logout() {
  localStorage.clear()
  router.push('/login')
}

/* ================= 筛选切换 ================= */
function setFilter(filter: string) {
  currentFilter.value = filter
  // 提取表达式为变量，解决TS模板字符串解析问题
  const filterIndex = ['all', 'lost', 'found'].indexOf(filter) + 1
  // 更新标签激活状态
  document.querySelectorAll('.filter-tab').forEach(tab => {
    tab.classList.remove('active')
  })
  document.querySelector(`.filter-tab:nth-child(${filterIndex})`)?.classList.add('active')
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

/* 左侧导航栏：固定宽度，垂直布局，上下分组+中间公告 */
.left-nav {
  width: 280px;
  height: 100vh;
  position: fixed;
  top: 0;
  left: 0;
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-right: 2px solid rgba(166, 124, 82, 0.2);
  /* 简化内边距 */
  padding: 20px;
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
  border-radius: 16px;
  padding: 20px;
  border: 2px solid rgba(166, 124, 82, 0.15);
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  gap: 15px;
}

.user-avatar-container {
  position: relative;
  width: 60px;
  height: 60px;
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
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 150px;
}

.user-subtitle {
  font-family: "Comic Sans MS", cursive;
  font-size: 13px;
  color: rgba(166, 124, 82, 0.7);
}

/* 左侧上半区：核心导航组 */
.nav-top-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 10px;
}

/* 左侧导航按钮样式（左右布局） */
.left-nav-btn {
  background: transparent;
  border: none;
  display: flex;
  align-items: center;
  gap: 15px;
  cursor: pointer;
  padding: 16px 20px;
  border-radius: 12px;
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
  font-size: 24px;
  min-width: 30px;
  text-align: center;
}

.left-nav-btn .nav-text {
  flex: 1;
}

/* 左侧中间：公告栏 */
.left-notice-card {
  background: rgba(255, 255, 255, 0.35);
  backdrop-filter: blur(10px);
  border-radius: 18px;
  padding: 20px;
  border: 2px solid rgba(166, 124, 82, 0.25);
  margin: 10px 0;
  display: flex;
  flex-direction: column;
  /* 高度自适应设置 */
  max-height: 250px; /* 限制最大高度 */
  min-height: 120px; /* 确保最小高度 */
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
  margin-bottom: 10px;
  font-weight: 600;
  text-align: center;
  flex-shrink: 0; /* 标题不压缩 */
}

.left-notice-card .notice-desc {
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: rgba(166, 124, 82, 0.8);
  line-height: 1.5;
  text-align: center;
  margin-bottom: 15px;
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
  height: 50px;
  padding: 0 20px;
  border-radius: 12px;
  font-family: "Comic Sans MS", cursive;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  border: 2px solid transparent;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
  color: white;
  width: 100%;
}

.left-action-btn:hover {
  transform: translateX(5px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
}

.left-action-btn .btn-icon {
  font-size: 20px;
}

.logout-btn {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

/* 右侧主内容区：自适应宽度，避开左侧导航 */
.main-content {
  flex: 1;
  min-height: 100vh;
  padding: 25px 30px;
  margin-left: 280px;
  max-width: calc(100vw - 280px);
  box-sizing: border-box;
}

/* 筛选标签栏 */
.filter-section {
  background: rgba(255, 255, 255, 0.18);
  backdrop-filter: blur(15px);
  border-radius: 20px;
  padding: 15px 20px;
  border: 2px solid rgba(166, 124, 82, 0.15);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
  margin-bottom: 25px;
}

.filter-tabs {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.filter-tab {
  padding: 10px 20px;
  border-radius: 20px;
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
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

/* 瀑布流卡片基础样式 */
.waterfall-card {
  background: rgba(255, 255, 255, 0.35);
  backdrop-filter: blur(15px);
  border-radius: 18px;
  overflow: hidden;
  border: 2px solid rgba(166, 124, 82, 0.2);
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
  height: 180px;
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
  padding: 20px;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.card-name {
  font-family: "Comic Sans MS", "Marker Felt", cursive;
  font-size: 20px;
  color: #a67c52;
  margin-bottom: 12px;
  font-weight: 600;
  line-height: 1.3;
}

.card-info {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin-bottom: auto;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: rgba(166, 124, 82, 0.8);
}

.info-icon {
  font-size: 16px;
}

.card-footer {
  display: flex;
  justify-content: center;
  margin-top: 15px;
}

.detail-btn {
  padding: 10px 24px;
  border: none;
  border-radius: 12px;
  background: linear-gradient(to right, #f38181, #f77d5f);
  color: white;
  font-family: "Comic Sans MS", cursive;
  font-size: 15px;
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

  .left-action-btn .btn-icon {
    font-size: 16px;
  }

  /* 右侧主内容区 */
  .main-content {
    margin-left: 0;
    max-width: 100vw;
    padding: 20px 15px;
    padding-bottom: 90px; /* 给底部导航留空间 */
  }

  .waterfall-grid {
    grid-template-columns: 1fr;
    gap: 15px;
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
    width: 240px;
  }

  .main-content {
    margin-left: 240px;
    max-width: calc(100vw - 240px);
  }
  
  .user-nickname {
    max-width: 120px;
  }
}
</style>