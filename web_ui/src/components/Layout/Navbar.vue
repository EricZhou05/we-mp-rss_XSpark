<template>
    <a-layout-header class="navbar-center">
      <a-menu
        class="navbar-center__menu"
        mode="horizontal"
        :selected-keys="selectedKeys"
        @menu-item-click="handleMenuClick"
      >
      <a-menu-item key="/">
        <template #icon>
          <icon-home />
        </template>
        订阅管理
      </a-menu-item>
      <a-menu-item key="/tags">
        <template #icon>
          <icon-tag />
        </template>
        标签管理
      </a-menu-item>
      <a-menu-item key="/message-tasks">
        <template #icon>
          <icon-notification />
        </template>
        消息任务
      </a-menu-item>
      <a-menu-item key="/configs">
        <template #icon>
          <icon-settings />
        </template>
        配置信息
      </a-menu-item>
      <a-menu-item key="/sys-info">
        <template #icon>
          <icon-info-circle />
        </template>
        系统信息
      </a-menu-item>
       <!-- <a-menu-item key="/reader">
        <template #icon>
          <icon-read />
            阅读器
        </template>
      </a-menu-item> -->
    </a-menu>
  </a-layout-header>
</template>

<script setup lang="ts">
import { ref, watchEffect } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import TextIcon from '@/components/TextIcon.vue'
import { translatePage, setCurrentLanguage } from '@/utils/translate';

const router = useRouter()
const route = useRoute()
const selectedKeys = ref<string[]>(['/'])

watchEffect(() => {
  selectedKeys.value = [route.path]
  // translatePage()
})

const handleMenuClick = (key: string) => {
  router.push(key)
}
</script>

<style scoped>
.navbar-center {
  display: flex;
}

/* 让 a-menu 占满容器，避免溢出误判 */
.navbar-center__menu {
  width: 100% !important;
  padding: 0 !important;
}

/* 关键：居中内部容器（不同版本类名可能略有差异，全部覆盖） */
.navbar-center__menu :deep(.arco-menu-inner),
.navbar-center__menu :deep(.arco-menu-overflow),
.navbar-center__menu :deep(.arco-menu-overflow-wrap) {
  display: flex !important;
  justify-content: center !important;
}

/* 防止菜单项收缩、换行 */
.navbar-center__menu :deep(.arco-menu-item),
.navbar-center__menu :deep(.arco-menu-pop) {
  flex: 0 0 auto;
  white-space: nowrap;
}
</style>