<template>
  <a-layout class="app-container">
    <!-- 头部 -->
    <a-layout-header class="app-header" v-if="route.path !== '/login'">
      <div class="header-left">
        <div class="logo">
          <img :src="logo" alt="avatar" :width="35" style="margin-right:1rem;">
          <router-link to="/" style="margin-right: 10px;">{{ appTitle }}</router-link>
          <a-divider direction="vertical" />
          <a-tooltip v-if="hasLogined" :content="!haswxLogined ? '未授权，请扫码登录' : '点我扫码授权'" position="bottom">

            <icon-scan @click="showAuthQrcode()" :style="{ marginLeft: '10px', cursor: 'pointer', color: !haswxLogined ? '#f00' : '#000' }"/>
          </a-tooltip>
        </div>
      </div>
      <div class="header-right" v-if="hasLogined">
        <a-link href="/api/docs" target="_blank" style="margin-right: 20px;">Docs</a-link>

        <a-dropdown position="br" trigger="click">
          <div class="user-info">
            <a-avatar :size="36">
              <img v-if="userInfo.avatar" :src="userInfo.avatar" alt="avatar">
              <icon-user v-else />
            </a-avatar>
            <span class="username">{{ userInfo.username }}</span>
          </div>
          <template #content>
            <a-doption @click="goToEditUser">
              <template #icon><icon-user /></template>
              个人中心
            </a-doption>
            <a-doption @click="goToChangePassword">
              <template #icon><icon-lock /></template>
              修改密码
            </a-doption>
            <a-doption @click="showAuthQrcode">
              <template #icon><icon-scan /></template>
              扫码授权
            </a-doption>
            <a-doption @click="handleLogout">
              <template #icon><icon-user /></template>
              退出登录
            </a-doption>
          </template>
        </a-dropdown>
        <WechatAuthQrcode ref="qrcodeRef" />
        <a-modal v-model:visible="sponsorVisible" title="感谢支持" :footer="false" :style="{ zIndex: 1000 }" unmount-on-close>
          <div style="text-align: center;">
            <p>如果您觉得这个项目对您有帮助,请给Rachel来一杯Coffee吧~ </p>
            <img src="@/assets/images/sponsor.jpg" alt="赞赏码" style="max-width: 300px; margin-top: 20px;">
          </div>
        </a-modal>
      </div>
    </a-layout-header>

    <a-layout>

      <!-- 主内容区 -->
      <a-layout>
        <a-layout-content class="app-content">
          <router-view />
        </a-layout-content>
      </a-layout>
    </a-layout>
  </a-layout>
</template>

<script setup lang="ts">
import { ref,watchEffect, computed, onMounted, watch, provide } from 'vue'
import { Modal } from '@arco-design/web-vue/es/modal'
import {getSysInfo} from '@/api/sysinfo'

const sponsorVisible = ref(false)
const showSponsorModal = (e: Event) => {
  e.preventDefault()
  sponsorVisible.value = true
  console.log('Sponsor modal triggered') // 添加调试日志
}
import { useRouter, useRoute } from 'vue-router'
import { Message } from '@arco-design/web-vue'
import { getCurrentUser } from '@/api/auth'
import { logout } from '@/api/auth'
import WechatAuthQrcode from '@/components/WechatAuthQrcode.vue'

const qrcodeRef = ref()
const showAuthQrcode = () => {
  qrcodeRef.value?.startAuth()
}
provide('showAuthQrcode', showAuthQrcode)
const appTitle = computed(() => import.meta.env.VITE_APP_TITLE || '星火调研易')
const logo = ref("/static/logo.svg")
const router = useRouter()
const route = useRoute()
const collapsed = ref(false)
const userInfo = ref({
  username: '',
  avatar: ''
})
const haswxLogined = ref(false)
const hasLogined = ref(false)
const isAuthenticated = computed(() => {
  hasLogined.value = !!localStorage.getItem('token')
  return hasLogined.value
})

const fetchUserInfo = async () => {
  try {
    const res = await getCurrentUser()
    userInfo.value = res
  } catch (error) {
    console.error('获取用户信息失败', error)
  }
}

const fetchSysInfo = async () => {
  try {
    const res = await getSysInfo()
    haswxLogined.value = res?.wx?.login||false
  } catch (error) {
    console.error('获取系统信息失败', error)
  }
}

const handleCollapse = (val: boolean) => {
  collapsed.value = val
}

const handleMenuClick = (key: string) => {
  router.push({ name: key })
}

const goToEditUser = () => {
  router.push({ name: 'EditUser' })
}

const goToChangePassword = () => {
  router.push({ name: 'ChangePassword' })
}

const handleLogout = async () => {
  try {
    await logout()
    localStorage.removeItem('token')
    router.push('/login')
  } catch (error) {
    Message.error('退出登录失败')
  }
}

onMounted(() => {
  if (isAuthenticated.value) {
    fetchUserInfo()
  }
  fetchSysInfo();
})

watch(
  () => route.path,
  () => {
    hasLogined.value = !!localStorage.getItem('token')
    if (hasLogined.value) {
      fetchUserInfo()
    }
  }
)
</script>

<style scoped>
.app-container {
  min-height: 100vh;
}


.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  height: 64px;
  background: var(--color-bg-2);
  border-bottom: 1px solid var(--color-border);
}

.header-left {
  display: flex;
  align-items: center;
}

.logo a {
  font-weight: bold;
  color: black;
  text-decoration: none;
}

.logo a:hover {
  color: #333;
}

.logo {
  display: flex;
  align-items: center;
  font-size: 18px;
  font-weight: 500;
}

.logo .arco-divider-vertical {
  margin: 0 14px;
  height: 1.8em;
}

.logo svg {
  margin-right: 10px;
  font-size: 24px;
  color: var(--primary-color);
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.username {
  margin-left: 10px;
}

.app-content {
  /* padding: 20px; */
  background: var(--color-bg-1);
  min-height: calc(100vh - 64px);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@media (max-width: 720px) {
  .app-header .header-right {
    display: none !important;
  }
}
</style>