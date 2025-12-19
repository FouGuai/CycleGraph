<template>
    <div class="login-container">
        <!-- 背景装饰 -->
        <div class="background-decoration">
            <div class="circle circle-1"></div>
            <div class="circle circle-2"></div>
            <div class="circle circle-3"></div>
        </div>

        <!-- 登录卡片 -->
        <div class="login-card">
            <!-- Logo 区域 -->
            <div class="logo-section">
                <div class="logo-icon">
                    <el-icon :size="48">
                        <Connection />
                    </el-icon>
                </div>
                <h1 class="system-title">CycleGraph</h1>
                <p class="system-subtitle">图数据库管理系统</p>
            </div>

            <!-- 表单区域 -->
            <el-tabs v-model="activeTab" class="login-tabs" stretch>
                <!-- 登录标签页 -->
                <el-tab-pane label="登录" name="login">
                    <el-form ref="loginFormRef" :model="loginForm" :rules="loginRules" class="login-form"
                        @keyup.enter="handleLogin">
                        <el-form-item prop="username">
                            <el-input v-model="loginForm.username" placeholder="请输入用户名" size="large" :prefix-icon="User"
                                clearable />
                        </el-form-item>
                        <el-form-item prop="password">
                            <el-input v-model="loginForm.password" type="password" placeholder="请输入密码" size="large"
                                :prefix-icon="Lock" show-password clearable />
                        </el-form-item>
                        <el-form-item>
                            <el-button type="primary" size="large" :loading="loginLoading" @click="handleLogin"
                                class="submit-button">
                                <span v-if="!loginLoading">登录</span>
                                <span v-else>登录中...</span>
                            </el-button>
                        </el-form-item>
                    </el-form>
                </el-tab-pane>

                <!-- 注册标签页 -->
                <el-tab-pane label="注册" name="register">
                    <el-form ref="registerFormRef" :model="registerForm" :rules="registerRules" class="login-form"
                        @keyup.enter="handleRegister">
                        <el-form-item prop="username">
                            <el-input v-model="registerForm.username" placeholder="请输入用户名" size="large"
                                :prefix-icon="User" clearable />
                        </el-form-item>
                        <el-form-item prop="password">
                            <el-input v-model="registerForm.password" type="password" placeholder="请输入密码" size="large"
                                :prefix-icon="Lock" show-password clearable />
                        </el-form-item>
                        <el-form-item prop="confirmPassword">
                            <el-input v-model="registerForm.confirmPassword" type="password" placeholder="请确认密码"
                                size="large" :prefix-icon="Lock" show-password clearable />
                        </el-form-item>
                        <el-form-item>
                            <el-button type="primary" size="large" :loading="registerLoading" @click="handleRegister"
                                class="submit-button">
                                <span v-if="!registerLoading">注册</span>
                                <span v-else>注册中...</span>
                            </el-button>
                        </el-form-item>
                    </el-form>
                </el-tab-pane>
            </el-tabs>

            <!-- 页脚信息 -->
            <div class="footer-info">
                <p>CycleGraph © 2025</p>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, Connection } from '@element-plus/icons-vue'
import { executeCommand } from '@/api/graph'

const router = useRouter()
const activeTab = ref('login')

// 设置 Cookie 的辅助函数
const setCookie = (name, value, days = 7) => {
  const expires = new Date()
  expires.setTime(expires.getTime() + days * 24 * 60 * 60 * 1000)
  document.cookie = `${name}=${value};expires=${expires.toUTCString()};path=/`
}

// 登录表单
const loginFormRef = ref()
const loginForm = reactive({
    username: '',
    password: ''
})

const loginRules = {
    username: [
        { required: true, message: '请输入用户名', trigger: 'blur' },
        { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }
    ],
    password: [
        { required: true, message: '请输入密码', trigger: 'blur' },
        { min: 6, message: '密码长度不能少于 6 个字符', trigger: 'blur' }
    ]
}

const loginLoading = ref(false)

// 注册表单
const registerFormRef = ref()
const registerForm = reactive({
    username: '',
    password: '',
    confirmPassword: ''
})

const validateConfirmPassword = (rule, value, callback) => {
    if (value === '') {
        callback(new Error('请再次输入密码'))
    } else if (value !== registerForm.password) {
        callback(new Error('两次输入密码不一致'))
    } else {
        callback()
    }
}

const registerRules = {
    username: [
        { required: true, message: '请输入用户名', trigger: 'blur' },
        { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' },
        { pattern: /^[a-zA-Z0-9_]+$/, message: '用户名只能包含字母、数字和下划线', trigger: 'blur' }
    ],
    password: [
        { required: true, message: '请输入密码', trigger: 'blur' },
        { min: 6, max: 30, message: '密码长度在 6 到 30 个字符', trigger: 'blur' }
    ],
    confirmPassword: [
        { required: true, message: '请确认密码', trigger: 'blur' },
        { validator: validateConfirmPassword, trigger: 'blur' }
    ]
}

const registerLoading = ref(false)

// 处理登录
const handleLogin = async () => {
    if (!loginFormRef.value) return

    await loginFormRef.value.validate(async (valid) => {
        if (!valid) return

        loginLoading.value = true
        try {
            const response = await executeCommand([
                'login',
                '-u',
                loginForm.username,
                '-p',
                loginForm.password
            ])

            if (response.status === 'success') {
                // 保存 token 到 cookie
                setCookie('token', 'logged_in_token', 7) // 保存7天
                // 保存用户名到 localStorage
                localStorage.setItem('username', loginForm.username)
                
                ElMessage.success('登录成功！')
                
                // 跳转到图查询页面
                await router.push('/query')
            } else {
                ElMessage.error(response.message || '登录失败，请检查用户名和密码')
            }
        } catch (error) {
            console.error('Login error:', error)
            ElMessage.error('登录请求失败，请检查网络连接')
        } finally {
            loginLoading.value = false
        }
    })
}

// 处理注册
const handleRegister = async () => {
    if (!registerFormRef.value) return

    await registerFormRef.value.validate(async (valid) => {
        if (!valid) return

        registerLoading.value = true
        try {
            const response = await executeCommand([
                'register',
                '-u',
                registerForm.username,
                '-p',
                registerForm.password
            ])

            if (response.status === 'success') {
                ElMessage.success('注册成功！请登录')
                // 保存用户名用于填充登录表单
                const registeredUsername = registerForm.username
                // 切换到登录标签页
                activeTab.value = 'login'
                // 将用户名填充到登录表单
                loginForm.username = registeredUsername
                // 清空注册表单
                registerForm.username = ''
                registerForm.password = ''
                registerForm.confirmPassword = ''
                registerFormRef.value.resetFields()
            } else {
                ElMessage.error(response.message || '注册失败，请重试')
            }
        } catch (error) {
            console.error('Register error:', error)
            ElMessage.error('注册请求失败，请检查网络连接')
        } finally {
            registerLoading.value = false
        }
    })
}
</script>

<style scoped>
.login-container {
    position: relative;
    width: 100vw;
    height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    overflow: hidden;
}

/* 背景装饰 */
.background-decoration {
    position: absolute;
    width: 100%;
    height: 100%;
    overflow: hidden;
}

.circle {
    position: absolute;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.1);
    animation: float 20s infinite ease-in-out;
}

.circle-1 {
    width: 300px;
    height: 300px;
    top: -100px;
    left: -100px;
    animation-delay: 0s;
}

.circle-2 {
    width: 400px;
    height: 400px;
    bottom: -150px;
    right: -150px;
    animation-delay: 2s;
}

.circle-3 {
    width: 200px;
    height: 200px;
    top: 50%;
    left: 50%;
    animation-delay: 4s;
}

@keyframes float {

    0%,
    100% {
        transform: translate(0, 0) scale(1);
    }

    33% {
        transform: translate(30px, -50px) scale(1.1);
    }

    66% {
        transform: translate(-20px, 20px) scale(0.9);
    }
}

/* 登录卡片 */
.login-card {
    position: relative;
    width: 480px;
    background: rgba(255, 255, 255, 0.98);
    border-radius: 20px;
    padding: 48px 40px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    backdrop-filter: blur(10px);
    animation: slideUp 0.6s ease-out;
}

@keyframes slideUp {
    from {
        opacity: 0;
        transform: translateY(50px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Logo 区域 */
.logo-section {
    text-align: center;
    margin-bottom: 40px;
}

.logo-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 80px;
    height: 80px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 20px;
    color: white;
    margin-bottom: 16px;
    box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
}

.system-title {
    font-size: 32px;
    font-weight: 700;
    color: #1a1a1a;
    margin: 0 0 8px 0;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.system-subtitle {
    font-size: 14px;
    color: #666;
    margin: 0;
    font-weight: 400;
}

/* 标签页 */
.login-tabs {
    margin-bottom: 24px;
}

.login-tabs :deep(.el-tabs__header) {
    margin-bottom: 32px;
}

.login-tabs :deep(.el-tabs__item) {
    font-size: 16px;
    font-weight: 500;
    color: #666;
}

.login-tabs :deep(.el-tabs__item.is-active) {
    color: #667eea;
    font-weight: 600;
}

.login-tabs :deep(.el-tabs__active-bar) {
    background-color: #667eea;
    height: 3px;
}

/* 表单样式 */
.login-form {
    margin-top: 8px;
}

.login-form :deep(.el-form-item) {
    margin-bottom: 24px;
}

.login-form :deep(.el-input__wrapper) {
    padding: 12px 16px;
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    transition: all 0.3s;
}

.login-form :deep(.el-input__wrapper:hover) {
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
}

.login-form :deep(.el-input__wrapper.is-focus) {
    box-shadow: 0 4px 16px rgba(102, 126, 234, 0.25);
}

.login-form :deep(.el-input__inner) {
    font-size: 15px;
}

.submit-button {
    width: 100%;
    height: 48px;
    font-size: 16px;
    font-weight: 600;
    border-radius: 10px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: none;
    box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
    transition: all 0.3s;
}

.submit-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 32px rgba(102, 126, 234, 0.4);
}

.submit-button:active {
    transform: translateY(0);
}

/* 页脚信息 */
.footer-info {
    text-align: center;
    margin-top: 32px;
    padding-top: 24px;
    border-top: 1px solid #eee;
}

.footer-info p {
    font-size: 13px;
    color: #999;
    margin: 0;
}

/* 响应式优化 */
@media (max-width: 1200px) {
    .login-card {
        width: 440px;
        padding: 40px 32px;
    }
}

@media (min-width: 1600px) {
    .login-card {
        width: 520px;
        padding: 56px 48px;
    }

    .system-title {
        font-size: 36px;
    }

    .logo-icon {
        width: 90px;
        height: 90px;
    }
}
</style>