import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'

// 导入页面组件
import StrategyAgent from '../views/StrategyAgent.vue'
import Setting from '../views/Setting.vue'

/**
 * 路由配置项类型
 * 添加索引签名以兼容Vue Router的Record<PropertyKey, unknown>类型要求
 */
interface MetaInfo {
  title?: string
  [key: string]: unknown
}

/**
 * 创建路由配置
 * @returns 路由实例
 */
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/agent/StrategyAgent',
      name: 'StrategyAgent',
      component: StrategyAgent,
      meta: {
        title: '策略代理'
      }
    },
    {
      path: '/setting',
      name: 'Setting',
      component: Setting,
      meta: {
        title: '系统设置'
      }
    },
    // 默认重定向到策略代理页面
    {
      path: '/',
      redirect: '/agent/StrategyAgent'
    }
  ]
})

// 全局前置守卫 - 设置页面标题
router.beforeEach((to, from, next) => {
  // 安全地获取和设置页面标题
  const meta = to.meta as MetaInfo;
  if (meta && meta.title) {
    document.title = meta.title || 'Vue3 App'
  }
  next()
})

export default router