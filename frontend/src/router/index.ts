import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'

/**
 * 路由表
 */
const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'Root',
    redirect: '/login' 
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/login/LoginView.vue'),
    meta: {
      title: '登录'
    }
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
    redirect: '/login'
  }
]

/**
 * 创建路由实例
 */
const router = createRouter({
  history: createWebHistory(),
  routes,
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

  // 需要登录的页面
  if (to.meta.requiresAuth) {
    const userId = localStorage.getItem('userId')
    const role = localStorage.getItem('role')

    if (userId && role) {
      next()
      return
    }

    // 未登录，记录返回地址
    localStorage.setItem('returnUrl', to.fullPath)
    next('/login')
    return
  }

  // 已登录却访问登录页
  if (to.path === '/login') {
    const userId = localStorage.getItem('userId')
    const role = localStorage.getItem('role')

    if (userId && role) {
      const returnUrl = localStorage.getItem('returnUrl')
      if (returnUrl) {
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
router.afterEach((to) => {
  console.log(`页面加载完成: ${to.path}`)
})

export default router
