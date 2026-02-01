import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'

/**
 * 路由表
 */
const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'Root',
    redirect: '/home'
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
      requiresAuth: true,
      title: '发现'
    }
  },
  {
    path: '/publish',
    name: 'Publish',
    component: () => import('../views/home/PublishView.vue'),
    meta: {
      requiresAuth: true,
      title: '发布'
    }
  },
  {
    path: '/messages',
    name: 'Messages',
    component: () => import('../views/home/MessagesView.vue'),
    meta: {
      requiresAuth: true,
      title: '消息'
    }
  },
  {
    path: '/my-posts',
    name: 'MyPosts',
    component: () => import('../views/home/MyPostsView.vue'),
    meta: {
      requiresAuth: true,
      title: '我的'
    }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('../views/home/SettingsView.vue'),
    meta: {
      requiresAuth: true,
      title: '设置'
    }
  },
  {
    path: '/item/detail',
    name: 'ItemDetail',
    component: () => import('../views/home/ItemDetailView.vue'),
    meta: {
      requiresAuth: true,
      title: '物品详情'
    }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    redirect: '/home'
  }
]

/**
 * 创建路由实例
 */
const router = createRouter({
  history: createWebHistory(),
  routes,
  // 路由切换时的滚动行为
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

/**
 * 全局前置路由守卫
 */
router.beforeEach((to, from, next) => {
  console.log(`路由跳转: ${from.path} -> ${to.path}`)
  
  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - 校园失物招领平台`
  } else {
    document.title = '校园失物招领平台'
  }
  
  // 检查是否需要登录权限
  if (to.meta.requiresAuth) {
    // 从localStorage获取用户信息
    const userId = localStorage.getItem('userId')
    const role = localStorage.getItem('role')
    
    // 检查用户信息是否完整
    if (userId && role) {
      // 已登录，允许访问
      next()
      return
    }
    
    // 未登录或用户信息不完整，重定向到登录页
    // 保存目标路径，以便登录后跳转回来
    const returnUrl = to.fullPath
    if (returnUrl !== '/login') {
      localStorage.setItem('returnUrl', returnUrl)
    }
    
    next('/login')
    return
  }
  
  // 如果已经登录但访问登录页，重定向到首页
  if (to.path === '/login') {
    const userId = localStorage.getItem('userId')
    const role = localStorage.getItem('role')
    
    if (userId && role) {
      // 已登录，重定向到首页或保存的returnUrl
      const returnUrl = localStorage.getItem('returnUrl')
      if (returnUrl && returnUrl !== '/login') {
        localStorage.removeItem('returnUrl')
        next(returnUrl)
      } else {
        next('/home')
      }
      return
    }
  }
  
  next()
})

/**
 * 全局后置路由守卫
 */
router.afterEach((to, from) => {
  // 可以在这里添加页面访问统计等
  console.log(`页面加载完成: ${to.path}`)
})

export default router