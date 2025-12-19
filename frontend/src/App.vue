<template>
  <div id="app">
    <el-container>
      <!-- 只在非登录页显示导航栏 -->
      <el-header v-if="!isLoginPage">
        <div class="header-content">
          <div class="logo">
            <el-icon :size="24"><Grid /></el-icon>
            <span>CycleGraph</span>
          </div>
          <div class="header-right">
            <div class="user-info">
              <el-dropdown @command="handleUserCommand">
                <span class="user-dropdown">
                  <el-icon><User /></el-icon>
                  <span class="username">{{ currentUser || '用户' }}</span>
                  <el-icon class="el-icon--right"><ArrowDown /></el-icon>
                </span>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="logout">
                      <el-icon><SwitchButton /></el-icon>
                      退出登录
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>
        </div>
      </el-header>
      <el-main :class="{ 'no-header': isLoginPage }">
        <router-view />
      </el-main>
      <el-footer v-if="!isLoginPage">
        <div class="footer-content">
          © 2025 CycleGraph - 图查询系统
        </div>
      </el-footer>
    </el-container>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Grid, User, ArrowDown, SwitchButton } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { whoami, logout } from '@/api/graph'

const route = useRoute()
const router = useRouter()
const activeRoute = computed(() => route.path)
const isLoginPage = computed(() => route.path === '/login')
const currentUser = ref('')

// 获取当前用户信息
const getCurrentUser = async () => {
  if (isLoginPage.value) return
  
  try {
    const response = await whoami()
    if (response.status === 'success' && response.current_user) {
      currentUser.value = response.current_user
    }
  } catch (error) {
    console.error('获取用户信息失败:', error)
  }
}

// 处理用户下拉菜单命令
const handleUserCommand = async (command) => {
  if (command === 'logout') {
    try {
      await logout()
      ElMessage.success('退出登录成功')
      router.push('/login')
    } catch (error) {
      console.error('退出登录失败:', error)
      ElMessage.error('退出登录失败')
    }
  }
}

onMounted(() => {
  getCurrentUser()
})
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB',
    'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
}

#app {
  height: 100vh;
}

.el-container {
  height: 100%;
}

.el-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  display: flex;
  align-items: center;
  padding: 0 30px;
  box-shadow: 0 2px 12px rgba(102, 126, 234, 0.3);
}

.header-content {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 30px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 22px;
  font-weight: 700;
  color: #fff;
  cursor: pointer;
}

.header-menu {
  background-color: transparent;
  border: none;
  flex: 0;
}

.header-menu .el-menu-item {
  color: #fff !important;
  border-bottom: 2px solid transparent;
  font-weight: 500;
}

.header-menu .el-menu-item:hover,
.header-menu .el-menu-item.is-active {
  background-color: rgba(255, 255, 255, 0.15) !important;
  border-bottom-color: #fff;
}

.user-info {
  display: flex;
  align-items: center;
}

.user-dropdown {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #fff;
  cursor: pointer;
  padding: 8px 16px;
  border-radius: 8px;
  transition: all 0.3s;
  background-color: rgba(255, 255, 255, 0.1);
}

.user-dropdown:hover {
  background-color: rgba(255, 255, 255, 0.2);
}

.username {
  font-size: 14px;
  font-weight: 500;
}

.el-main {
  background-color: #f0f2f5;
  padding: 20px;
  overflow-y: auto;
}

.el-main.no-header {
  padding: 0;
  background-color: transparent;
}

.el-footer {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 40px;
  box-shadow: 0 -2px 12px rgba(102, 126, 234, 0.2);
}

.footer-content {
  text-align: center;
  font-size: 14px;
}
</style>
