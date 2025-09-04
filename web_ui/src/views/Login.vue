<template>
  <div class="login-container">
    <div class="login-layout">
      <!-- 左侧介绍区域 -->
      <div class="login-left">
        <div class="login-intro">
          <h1 class="intro-title">{{appTitle}}</h1>
          <p class="intro-text">
            一个用于订阅和管理微信公众号内容的工具，提供RSS订阅功能
          </p>
          <div class="login-features">
            <div class="feature-item">
              <icon-check-circle />
              <span>公众号内容抓取和解析</span>
            </div>
            <div class="feature-item">
              <icon-check-circle />
              <span>RSS订阅生成</span>
            </div>
            <div class="feature-item">
              <icon-check-circle />
              <span>定时自动更新内容</span>
            </div>
            <div class="feature-item">
              <icon-check-circle />
              <span>公众号监测、消息通知、WebHook调用 </span>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧登录区域 -->
      <div class="login-right">
        <a-card class="login-card" :bordered="false">
          <a-form :model="form" @submit="handleSubmit">
            <a-form-item field="username" label="帐号">
              <a-input v-model="form.username" placeholder="请输入帐号">
                <template #prefix><icon-user /></template>
              </a-input>
            </a-form-item>

            <a-form-item field="password" label="密码">
              <a-input-password v-model="form.password" placeholder="请输入密码">
                <template #prefix><icon-lock /></template>
              </a-input-password>
            </a-form-item>

            <a-form-item>
              <a-button type="primary" html-type="submit" :loading="loading" long>
                登录
              </a-button>
            </a-form-item>
          </a-form>
        </a-card>
      </div>
    </div>
    <div class="login-footer">
      <div class="copyright">Design By Rachel</div>
      <div class="footer-links">
        <a-link href="https://github.com/rachelos/we-mp-rss" target="_blank">GitHub</a-link>
        <span class="divider">|</span>
        <a-link href="https://gitee.com/rachel_os/we-mp-rss" target="_blank">Gitee</a-link>
        <span class="divider">|</span>
        <a-link href="/api/docs" target="_blank">Docs</a-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Message } from '@arco-design/web-vue'
import { login } from '@/api/auth'

const appTitle = computed(() => import.meta.env.VITE_APP_TITLE || '星火调研易')

const router = useRouter()
const loading = ref(false)
const form = ref({
  username: '',
  password: ''
})

const handleSubmit = async () => {
  loading.value = true
  try {
    const res = await login({
      username: form.value.username,
      password: form.value.password
    })

    if (res.access_token) {
      localStorage.setItem('token', res.access_token)
      localStorage.setItem('token_expire', Date.now() + (res.expires_in * 1000))

      const redirect = router.currentRoute.value.query.redirect
      await router.push(redirect ? redirect.toString() : '/')
      Message.success('登录成功')
    } else {
      throw new Error('无效的响应格式')
    }
  } catch (error) {
    console.error('登录错误:', error)
    const errorMsg = error.response?.data?.detail ||
                    error.response?.data?.message ||
                    error.message ||
                    '登录失败，请检查用户名和密码'
    Message.error(errorMsg)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* 1. 设置容器为动态渐变背景 */
.login-container {
  position: relative; /* 为 footer 提供定位上下文 */
  height: 100vh;
  overflow: hidden;
  padding: 0;
  margin: 0;
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.95) 0%, rgba(168, 85, 247, 0.9) 100%);
  background-size: 200% 200%;
  animation: gradientBG 12s ease infinite;
}

/* 移除了壁纸和 ::before 伪元素 */

@keyframes gradientBG {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}

.login-layout {
  display: flex;
  height: 100%;
  transition: all 0.3s ease;
  position: relative; /* 确保内容在背景之上 */
  z-index: 1;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 3. 左侧介绍区域，宽度占一半 */
.login-left {
  flex: 1; /* 使其与右侧平分空间 */
  padding: 80px;
  color: #ffffff;
  display: flex;
  flex-direction: column;
  justify-content: center;
  background: transparent; /* 背景透明以显示容器的渐变 */
}

.intro-title {
  animation: fadeInUp 0.8s ease-out both;
}

.intro-text {
  animation: fadeInUp 0.8s ease-out 0.2s both;
}

.feature-item {
  opacity: 0;
  animation: fadeInUp 0.6s ease-out forwards;
}

.feature-item:nth-child(1) {
  animation-delay: 0.4s;
}

.feature-item:nth-child(2) {
  animation-delay: 0.5s;
}

.feature-item:nth-child(3) {
  animation-delay: 0.6s;
}

.feature-item:nth-child(4) {
  animation-delay: 0.7s;
}

/* 4. 右侧登录区域，宽度占一半 */
.login-right {
  flex: 1; /* 使其与左侧平分空间 */
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 60px;
  background: transparent; /* 确保背景透明 */
}

.login-form {
  border: none;
  background: transparent;
  padding: 40px;
  border-radius: 12px;
}

.login-intro {
  max-width: 600px;
  margin-bottom: 60px;
}

.intro-title {
  font-size: 2.5rem;
  margin-bottom: 24px;
  font-weight: 600;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.intro-text {
  font-size: 1.1rem;
  line-height: 1.6;
  margin-bottom: 32px;
  opacity: 0.9;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.login-features {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 1rem;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.login-ad {
  margin-top: auto;
}

.login-ad img {
  width: 100%;
  max-width: 600px;
  border-radius: 8px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

/* 5. 登录卡片样式 - 添加毛玻璃效果 */
.login-card {
  width: 400px;
  padding: 40px;
  /* !!! 关键修改开始 !!! */
  /* 修改背景为半透明，让底层背景能透过来 */
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  /* 调整阴影以增强毛玻璃的浮动感 */
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.1);
  /* 添加半透明边框，让卡片边缘更清晰 */
  border: 1px solid rgba(255, 255, 255, 0.3);
  /* 应用毛玻璃效果 */
  backdrop-filter: blur(15px);
  -webkit-backdrop-filter: blur(15px); /* 兼容 Safari 浏览器 */
  /* !!! 关键修改结束 !!! */
  transition: all 0.3s ease;
}

.login-card:hover {
  transform: translateY(-5px);
  /* 调整鼠标悬停时的阴影效果 */
  box-shadow: 0 12px 48px 0 rgba(0, 0, 0, 0.2);
}


:deep(.arco-form-item-label) {
  color: #333 !important; /* 字体颜色可能需要调整，以便在毛玻璃背景上清晰显示 */
}

:deep(.arco-input-wrapper) {
  height: 48px;
  /* 调整输入框背景，如果需要适应毛玻璃效果 */
  background: rgba(255, 255, 255, 0.7); /* 可以尝试半透明 */
  border: 1px solid rgba(255, 255, 255, 0.3); /* 调整边框颜色 */
  border-radius: 8px;
  color: #1a202c;
  transition: all 0.2s ease;
}

:deep(.arco-input-wrapper:hover) {
  border-color: rgba(255, 255, 255, 0.5); /* 调整悬停边框颜色 */
  background: rgba(255, 255, 255, 0.8);
}

:deep(.arco-input-wrapper:focus-within) {
  border-color: #4299e1;
  box-shadow: 0 0 0 2px rgba(66, 153, 225, 0.2);
  background: #fff;
}

:deep(.arco-input::placeholder) {
  color: #a0aec0;
}

.login-title {
  text-align: center;
  margin-bottom: 32px;
}

.login-title h2 {
  color: #1a202c;
  font-weight: 600;
  font-size: 28px;
  letter-spacing: -0.5px;
  margin-bottom: 8px;
}

.login-title p {
  color: #4a5568;
  font-size: 15px;
  line-height: 1.5;
}

:deep(.arco-form-item-label) {
  color: #2d3748 !important;
  font-weight: 500;
  font-size: 15px;
  margin-bottom: 6px;
  display: block;
}

:deep(.arco-input-wrapper) {
  border-radius: 8px;
  transition: all 0.2s ease;
}

:deep(.arco-input-wrapper:hover) {
  border-color: #4299e1;
}

:deep(.arco-btn-primary) {
  height: 48px;
  border-radius: 8px;
  transition: all 0.2s ease;
  font-weight: 500;
  font-size: 15px;
  background: #4299e1;
  border-color: #4299e1;
  color: white;
}

:deep(.arco-btn-primary:hover) {
  background: #3182ce;
  border-color: #3182ce;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(66, 153, 225, 0.3);
}

:deep(.arco-btn-primary:active) {
  transform: translateY(0);
  box-shadow: none;
}

:deep(.arco-form-item-error .arco-input-wrapper) {
  border-color: #e53e3e;
  background-color: #fff5f5;
}

:deep(.arco-form-message) {
  color: #e53e3e;
  font-size: 13px;
  margin-top: 6px;
  display: flex;
  align-items: center;
}

:deep(.arco-form-message)::before {
  content: "!";
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  margin-right: 6px;
  background: #e53e3e;
  color: white;
  border-radius: 50%;
  font-size: 12px;
  font-weight: bold;
}

.login-footer {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  text-align: center;
  padding: 24px 0;
  color: #fff;
  font-size: 14px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  z-index: 10;
}

.login-footer a {
  color: #fff;
  text-decoration: none;
  transition: all 0.2s ease;
  font-size: 0.875rem;
  font-weight: 500;
  padding: 4px 8px;
  border-radius: 6px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.login-footer a:hover {
  color: #fff;
  background: rgba(66, 153, 225, 0.1);
  transform: translateY(-1px);
  text-decoration: none;
}

.copyright {
  font-size: 0.875rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
}

.copyright::before {
  content: "©";
  font-size: 0.75rem;
  opacity: 0.7;
}

.footer-links {
  display: flex;
  align-items: center;
  gap: 16px;
}

.divider {
  user-select: none;
}

.login-footer a {
  text-decoration: none;
  transition: all 0.2s ease;
  font-size: 0.875rem;
  font-weight: 500;
  padding: 4px 8px;
  border-radius: 6px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.login-footer a:hover {
  transform: translateY(-1px);
  text-decoration: none;
}

.login-footer a:active {
  transform: translateY(0);
}

.login-footer a::before {
  content: "";
  display: inline-block;
  width: 16px;
  height: 16px;
  background-size: contain;
  background-repeat: no-repeat;
  background-position: center;
}

.login-footer a[href*="github"]::before {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23ffffff'%3E%3Cpath d='M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12'/%3E%3C/svg%3E");
}

.login-footer a[href*="gitee"]::before {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23ffffff'%3E%3Cpath d='M11.984 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.016 0zm6.09 5.333c.328 0 .593.266.592.593v1.482a.594.594 0 0 1-.593.592H9.777c-.982 0-1.778.796-1.778 1.778v5.63c0 .327.266.592.593.592h5.63c.982 0 1.778-.796 1.778-1.778v-.296a.593.593 0 0 0-.592-.593h-4.15a.592.592 0 0 1-.592-.592v-1.482a.593.593 0 0 1 .593-.592h6.815c.327 0 .593.265.593.592v3.408a4 4 0 0 1-4 4H5.926a.593.593 0 0 1-.593-.593V9.778a4.444 4.444 0 0 1 4.445-4.444h8.296z'/%3E%3C/svg%3E");
}

.login-footer a[href*="docs"]::before {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23ffffff'%3E%3Cpath d='M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6zM6 4h7v5h5v11H6V4zm8 18v-1h4v1h-4zm-3 0v-1h1v1h-1zm-2 0v-1h1v1h-1zm-2 0v-1h1v1H7z'/%3E%3C/svg%3E");
}

/* 6. 修复手机版布局 */
@media (max-width: 992px) {
  .login-layout {
    flex-direction: column;
  }

  .login-left,
  .login-right {
    flex: 1; /* 让左右两部分平分高度 */
    width: 100%;
    flex-basis: auto; /* 重置flex-basis */
    padding: 40px;
  }

  .login-card {
    width: 100%;
    max-width: 400px;
  }

  .intro-title {
    font-size: 2rem;
  }

  .login-ad {
    display: none;
  }
}

@media (max-width: 720px) {
  .login-container .login-left .login-intro{
    font-size: 2rem !important;
    margin-bottom:0 !important;
  }
  .login-container .login-left .login-intro .login-features,.intro-text {
    display:none !important;
  }
  .login-container .login-right button {
    width: 60% !important;
  }
  .login-container .login-right {
    /* 确保在小屏幕上，右侧也能填满剩余空间 */
    flex-grow: 1;
    flex-shrink: 0;
  }
  .login-container .login-left {
     /* 调整左侧，使其内容收缩，留出更多空间给右侧 */
    flex-grow: 0;
    flex-shrink: 1;
    flex-basis: auto;
  }
  .login-container .login-card {
    width: 100% !important;
    padding: 20px !important; /* 保留一些内边距 */
  }
}
</style>