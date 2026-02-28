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
    path: '/force-change-password',
    name: 'ForceChangePassword',
    component: () => import('../views/home/ForceChangePassword.vue'),
    meta: {
      requiresAuth: true,
      title: '修改密码'
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
    path: '/admin/login',
    name: 'AdminLogin',
    component: () => import('../views/admin/AdminLoginView.vue'),
    meta: {
      title: '管理员登录'
    }
  },
  {
    path: '/admin/dashboard',
    name: 'AdminDashboard',
    component: () => import('../views/admin/AdminDashboard.vue'),
    meta: {
      requiresAuth: true,
      requiresAdmin: true,
      title: '管理员面板'
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
  scrollBehavior(_to, _from, savedPosition) {
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

  // ===== 需要登录的页面 =====
  if (to.meta.requiresAuth) {
    const userId = sessionStorage.getItem('userId')
    const role = sessionStorage.getItem('role')
    const firstLogin = sessionStorage.getItem('firstLogin')

    if (userId && role) {
      // 检查管理员权限
      if (to.meta.requiresAdmin && role !== '3') {
        // 非管理员访问管理员页面，跳转到普通用户首页
        next('/home')
        return
      }
      
      // 首次登录用户只能访问密码修改页面
      if (firstLogin === '1' && to.path !== '/force-change-password') {
        next('/force-change-password')
        return
      }
      
      next()
      return
    }

    // 未登录,记录返回地址(本次会话有效)
    sessionStorage.setItem('returnUrl', to.fullPath)
    
    // 管理员页面跳转到管理员登录页，普通页面跳转到普通登录页
    if (to.meta.requiresAdmin) {
      next('/admin/login')
    } else {
      next('/login')
    }
    return
  }

  // ===== 已登录却访问登录页 =====
  if (to.path === '/login') {
    const userId = sessionStorage.getItem('userId')
    const role = sessionStorage.getItem('role')

    if (userId && role) {
      const returnUrl = sessionStorage.getItem('returnUrl')
      if (returnUrl) {
        sessionStorage.removeItem('returnUrl')
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