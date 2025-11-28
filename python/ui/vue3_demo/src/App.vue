<template>
  <div class="app-container">
    <!-- 侧边栏导航 -->
    <aside class="side-nav">
      <!-- 侧边栏顶部品牌 -->
      <div class="nav-brand">
        <div class="brand-icon">
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
          </svg>
        </div>
      </div>

      <!-- 侧边栏菜单 -->
      <div class="nav-menu">
        <!-- 菜单项 - 策略代理 -->
        <router-link to="/agent/StrategyAgent" class="nav-item">
          <div class="nav-icon">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M19 3h-4.18C14.4 1.84 13.3 1 12 1c-1.3 0-2.4.84-2.82 2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-7 0c.55 0 1 .45 1 1s-.45 1-1 1-1-.45-1-1 .45-1 1-1zm-2 14l-4-4 1.41-1.41L10 14.17l6.59-6.59L18 9l-8 8z"/>
            </svg>
          </div>
          <span class="nav-text">策略代理</span>
        </router-link>

        <!-- 菜单项 - 其他功能图标 -->
        <div class="nav-item" @click="handleMenuClick('/ai-assistant')">
          <div class="nav-icon">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
            </svg>
          </div>
          <span class="nav-text">AI助手</span>
        </div>

        <div class="nav-item" @click="handleMenuClick('/data-stats')">
          <div class="nav-icon">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M3.5 18.49l6-6.01 4 4L22 6.92l-1.41-1.41-7.09 7.97-4-4L2 16.99l1.5 1.5z"/>
            </svg>
          </div>
          <span class="nav-text">数据统计</span>
        </div>

        <div class="nav-item" @click="handleMenuClick('/log-management')">
          <div class="nav-icon">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6zm-2 16c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1zm0-4c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1zm-2-5V3.5L18.5 9H12zm4 7c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1zm0-4c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1z"/>
            </svg>
          </div>
          <span class="nav-text">日志管理</span>
        </div>

        <div class="nav-item" @click="handleMenuClick('/news')">
          <div class="nav-icon">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M10.5 1C5.81 1 2 4.81 2 9.5S5.81 18 10.5 18 19 14.19 19 9.5 15.19 1 10.5 1zm0 15c-2.49 0-4.5-2.01-4.5-4.5S8.01 6 10.5 6 15 8.01 15 10.5 12.99 16 10.5 16zm0-11C9.12 5 8 6.12 8 7.5S9.12 10 10.5 10 13 8.88 13 7.5 11.88 5 10.5 5zm0 9C12.99 14 15 11.99 15 9.5S12.99 5 10.5 5 6 7.01 6 9.5 8.01 14 10.5 14z"/>
            </svg>
          </div>
          <span class="nav-text">新闻资讯</span>
        </div>

        <div class="nav-item" @click="handleMenuClick('/vr')">
          <div class="nav-icon">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M20 3H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h4l4 4 4-4h4c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 14H4V5h16v12z"/>
            </svg>
          </div>
          <span class="nav-text">虚拟现实</span>
        </div>

        <div class="nav-item" @click="handleMenuClick('/ai-ecosystem')">
          <div class="nav-icon">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
            </svg>
          </div>
          <span class="nav-text">AI生态</span>
        </div>
      </div>

      <!-- 设置按钮放在底部 -->
      <div class="nav-bottom">
        <router-link to="/setting" class="nav-item">
          <div class="nav-icon">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M19.14 12.94c.04-.3.06-.61.06-.94 0-.32-.02-.64-.07-.94l2.03-1.58c.18-.14.23-.41.12-.61l-1.92-3.32c-.12-.22-.37-.29-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54c-.04-.24-.24-.41-.48-.41h-3.84c-.24 0-.43.17-.47.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96c-.22-.08-.47 0-.59.22L2.74 8.87c-.12.21-.08.47.12.61l2.03 1.58c-.05.3-.09.63-.09.94s.02.64.07.94l-2.03 1.58c-.18.14-.23.41-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.47-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z"/>
            </svg>
          </div>
          <span class="nav-text">设置</span>
        </router-link>
      </div>
    </aside>

    <!-- 主内容区域 -->
    <main class="main-container">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>

    <!-- 页脚
    <footer class="main-footer">
      <div class="footer-content">
        <p>&copy; 2024 系统管理平台 | 版本 v1.0.0</p>
      </div>
    </footer> -->
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import { useRouter } from 'vue-router'

/**
 * 侧边栏导航组件
 * 功能：实现左侧图标菜单布局，支持鼠标悬停显示文字描述，设置按钮位于底部
 */
export default defineComponent({
  name: 'App',
  setup() {
    // 使用Vue Router
    const router = useRouter()
    
    /**
     * 处理菜单点击事件
     * @param {string} path - 路由路径
     */
    const handleMenuClick = (path: string): void => {
      router.push(path)
    }
    
    return {
      handleMenuClick
    }
  }
})
</script>

<style>
/* 全局样式重置 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
  line-height: 1.6;
  color: #333;
  background-color: #f5f7fa;
}

/* 应用容器 - 改为水平布局 */
.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: row;
}

/* 侧边栏样式 */
.side-nav {
  width: 70px;
  background-color: white;
  box-shadow: 2px 0 4px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0;
  left: 0;
  height: 100vh;
  z-index: 100;
  transition: width 0.3s ease;
  overflow: visible;
}

/* 侧边栏品牌区域 */
.nav-brand {
  padding: 20px 0;
  text-align: center;
  border-bottom: 1px solid #f0f0f0;
}

.brand-icon {
  width: 32px;
  height: 32px;
  margin: 0 auto;
  color: #4a6cf7;
}

.brand-icon svg {
  width: 100%;
  height: 100%;
}

/* 侧边栏菜单区域 */
.nav-menu {
  flex: 1;
  padding: 20px 0;
  overflow: visible;
}

/* 侧边栏底部区域 - 放置设置按钮 */
.nav-bottom {
  padding: 20px 0;
  border-top: 1px solid #f0f0f0;
  margin-top: auto;
}

/* 菜单项样式 */
.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16px 10px;
  color: #666;
  text-decoration: none;
  position: relative;
  transition: all 0.3s ease;
  cursor: pointer;
}

/* 图标样式 */
.nav-icon {
  width: 24px;
  height: 24px;
  margin-bottom: 5px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.nav-icon svg {
  width: 100%;
  height: 100%;
}

/* 文字描述 - 默认隐藏 */
.nav-text {
  font-size: 12px;
  opacity: 0;
  position: absolute;
  left: 100%;
  top: 50%;
  transform: translateY(-50%);
  background-color: #333;
  color: white;
  padding: 6px 12px;
  border-radius: 4px;
  white-space: nowrap;
  z-index: 1000;
  pointer-events: none;
  transition: opacity 0.3s ease;
  margin-left: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

/* 文字描述箭头 */
.nav-text::before {
  content: '';
  position: absolute;
  right: 100%;
  top: 50%;
  transform: translateY(-50%);
  border-style: solid;
  border-width: 5px 5px 5px 0;
  border-color: transparent #333 transparent transparent;
}

/* 鼠标悬停效果 */
.nav-item:hover {
  background-color: #f0f4ff;
  color: #4a6cf7;
}

/* 鼠标悬停显示文字描述 */
.nav-item:hover .nav-text {
  opacity: 1;
}

/* 激活状态样式 */
.nav-item.router-link-active {
  background-color: #f0f4ff;
  color: #4a6cf7;
}

.nav-item.router-link-active .nav-icon {
  transform: scale(1.1);
}

/* 主内容区域 - 调整为侧边栏布局 */
.main-container {
  flex: 1;
  margin-left: 70px;
  padding: 20px;
  min-height: 100vh;
}

/* 页脚样式 */
.main-footer {
  background-color: white;
  border-top: 1px solid #e0e0e0;
  padding: 20px;
  margin-left: 70px;
}

.footer-content {
  text-align: center;
  font-size: 14px;
  color: #666;
}

/* 页面过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .side-nav {
    width: 60px;
  }
  
  .main-container,
  .main-footer {
    margin-left: 60px;
  }
  
  .main-container {
    padding: 15px;
  }
  
  .nav-item {
    padding: 12px 8px;
  }
}  
</style>