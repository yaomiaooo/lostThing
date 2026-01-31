import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'

/**
 * 路由表
 */
const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/login/LoginView.vue')
  },
  {
    path: '/home',
    name: 'Home',
    component: () => import('../views/home/HomeView.vue'),
    meta: {
      requiresAuth: true
    }
  }
]

/**
 * 创建路由实例
 */
const router = createRouter({
  history: createWebHistory(),
  routes
})

/**
 * 全局前置路由守卫
 */
router.beforeEach((to, from, next) => {
  // 是否需要登录
  if (to.meta.requiresAuth) {
    const userId = localStorage.getItem('userId')
    if (!userId) {
      next('/login')
      return
    }
  }
  next()
})

export default router
