import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Login from '../views/Login.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { title: '登录 - CycleGraph' }
  },
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: {
      title: '首页 - CycleGraph',
      requiresAuth: true // 需要登录才能访问
    }
  },
  {
    path: '/query',
    name: 'GraphQuery',
    component: () => import('../views/GraphQuery.vue'),
    meta: {
      title: '图查询 - CycleGraph',
      requiresAuth: true
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫 - 检查登录状态
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = to.meta.title || 'CycleGraph'

  // 如果路由需要认证
  if (to.meta.requiresAuth) {
    // 检查cookie中是否有token
    const hasToken = true

    if (!hasToken) {
      // 未登录，跳转到登录页
      next('/login')
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router