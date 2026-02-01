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
  },
  {
    path: '/publish',
    name: 'Publish',
    component: () => import('../views/home/PublishView.vue'),
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
  // 如果需要登录权限
  if (to.meta.requiresAuth) {
    const userId = localStorage.getItem('userId')
    const role = localStorage.getItem('role')
    
    // 检查用户是否已登录
    if (!userId || !role) {
      // 清除可能存在的过期登录信息
      localStorage.removeItem('userId')
      localStorage.removeItem('realName')
      localStorage.removeItem('role')
      localStorage.removeItem('loginTime')
      
      // 重定向到登录页
      next('/login')
      return
    }
  }
  
  // 如果已经登录但访问登录页，重定向到首页
  if (to.path === '/login') {
    const userId = localStorage.getItem('userId')
    const role = localStorage.getItem('role')
    
    if (userId && role) {
      next('/home')
      return
    }
  }
  
  next()
})



export default router