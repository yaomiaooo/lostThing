<!-- src/views/item-admin/index.vue -->
<template>
  <div class="admin-layout">
    <!-- 纯色背景 -->
    <div class="background-container">
      <div class="solid-background"></div>
    </div>

    <!-- 左侧导航栏 - 只在这里渲染一次 -->
    <AdminNavigation 
      :subtitle="currentSubtitle"
      :active-nav="currentActiveNav"
      :show-stats-card="showStatsCard"
      @logout="handleLogout"
    />

    <!-- 右侧主内容区域 - 子路由在这里渲染 -->
    <main class="main-content">
      <router-view v-slot="{ Component }">
        <!-- 使用淡入淡出动画，避免重影 -->
        <transition name="fade" mode="out-in">
          <component :is="Component" :key="$route.path" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AdminNavigation from './components/AdminNavigation.vue'

const route = useRoute()
const router = useRouter()

// 根据当前路由计算副标题
const currentSubtitle = computed(() => {
  const subtitleMap: Record<string, string> = {
    '/item-admin/notices': '请确认公告',
    '/item-admin/pending': '请审核信息',
    '/item-admin/items': '管理物品状态',
    '/item-admin/statistics': '查看统计数据',
    '/item-admin/history': '查询历史记录'
  }
  return subtitleMap[route.path] || '欢迎回来^_^'
})

// 根据当前路由计算活动导航
const currentActiveNav = computed(() => {
  return (route.meta.activeNav as string) || ''
})

// 是否显示统计卡片（只在公告页和首页显示）
const showStatsCard = computed(() => {
  return route.path === '/item-admin/notices' || route.path === '/item-admin/pending'
})

// 退出登录
const handleLogout = () => {
  router.push('/login')
}
</script>

<style scoped>
.admin-layout {
  width: 100vw;
  min-height: 100vh;
  position: relative;
  overflow-x: hidden;
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

.solid-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: #f8f3d4;
  pointer-events: none;
}

/* 右侧主内容区 */
.main-content {
  position: relative;
  z-index: 2;
  flex: 1;
  min-height: 100vh;
  padding: 24px 28px;
  margin-left: 288px;
  max-width: calc(100vw - 288px);
  box-sizing: border-box;
}

/* 页面切换动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.fade-enter-from {
  opacity: 0;
  transform: translateX(10px);
}

.fade-leave-to {
  opacity: 0;
  transform: translateX(-10px);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .main-content {
    margin-left: 0;
    max-width: 100vw;
    padding: 20px 15px;
    padding-bottom: 100px;
  }
}
</style>