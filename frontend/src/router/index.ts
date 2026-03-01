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
      title: '发现',
      allowedRoles: [1]  // 普通用户
    }
  },
  {
    path: '/publish',
    name: 'Publish',
    component: () => import('../views/home/PublishView.vue'),
    meta: {
      requiresAuth: true,
      title: '发布',
      allowedRoles: [1]
    }
  },
  {
    path: '/messages',
    name: 'Messages',
    component: () => import('../views/home/MessagesView.vue'),
    meta: {
      requiresAuth: true,
      title: '消息',
      allowedRoles: [1]
    }
  },
  {
    path: '/my-posts',
    name: 'MyPosts',
    component: () => import('../views/home/MyPostsView.vue'),
    meta: {
      requiresAuth: true,
      title: '我的',
      allowedRoles: [1]
    }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('../views/home/SettingsView.vue'),
    meta: {
      requiresAuth: true,
      title: '设置',
      allowedRoles: [1]
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

  // ==================== 失物招领管理员端 ====================

  {
    path: '/item-admin/notices',
    name: 'AdminNotices',
    component: () => import('../views/item-admin/pages/NoticeView.vue'),
    meta: {
      requiresAuth: true,
      allowedRoles: [3],
      title: '通知公告',
      activeNav: '通知公告',
      subtitle: '请确认公告'
    }
  },
  {
    path: '/item-admin/pending',
    name: 'AdminPending',
    component: () => import('../views/item-admin/pages/PendingReviewView.vue'),
    meta: {
      requiresAuth: true,
      allowedRoles: [3],
      title: '待审核',
      activeNav: '待审核',
      subtitle: '请审核信息'
    }
  },
  {
    path: '/item-admin/items',
    name: 'AdminItems',
    component: () => import('../views/item-admin/pages/ItemManageView.vue'),
    meta: {
      requiresAuth: true,
      allowedRoles: [3],
      title: '物品管理',
      activeNav: '物品管理',
      subtitle: '管理物品状态'
    }
  },
  {
    path: '/item-admin/statistics',
    name: 'AdminStatistics',
    component: () => import('../views/item-admin/pages/StatisticsView.vue'),
    meta: {
      requiresAuth: true,
      allowedRoles: [3],
      title: '数据统计',
      activeNav: '数据统计',
      subtitle: '查看统计数据'
    }
  },
  {
    path: '/item-admin/history',
    name: 'AdminHistory',
    component: () => import('../views/item-admin/pages/HistoryQueryView.vue'),
    meta: {
      requiresAuth: true,
      allowedRoles: [3],
      title: '历史查询',
      activeNav: '历史查询',
      subtitle: '查询历史记录'
    }
  },

  // 404 页面
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

  // 获取登录信息
  const userId = sessionStorage.getItem('userId')
  const role = sessionStorage.getItem('role')
  const firstLogin = sessionStorage.getItem('firstLogin')
  const userRole = role ? parseInt(role) : 0

  // ===== 需要登录的页面 =====
  if (to.meta.requiresAuth) {
    if (!userId || !role) {
      // 未登录，记录返回地址
      sessionStorage.setItem('returnUrl', to.fullPath)
      next('/login')
      return
    }

    // 首次登录强制修改密码
    if (firstLogin === '1' && to.path !== '/force-change-password') {
      next('/force-change-password')
      return
    }

    // 检查角色权限
    if (to.meta.allowedRoles) {
      const allowedRoles = to.meta.allowedRoles as number[]
      if (!allowedRoles.includes(userRole)) {
        // 无权限，根据角色跳转
        if (userRole === 1) {
          next('/home')  // 普通用户去首页
        } else if (userRole === 3 || userRole === 4) {
          next('/item-admin/notices')  // 管理员去管理端
        } else {
          next('/login')
        }
        return
      }
    }

    next()
    return
  }

  // ===== 已登录却访问登录页 =====
  if (to.path === '/login') {
    if (userId && role) {
      // 已登录，根据角色跳转
      if (userRole === 1) {
        next('/home')
      } else if (userRole === 3 || userRole === 4) {
        next('/item-admin/notices')
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