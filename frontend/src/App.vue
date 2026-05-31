<script setup lang="ts">
import { onMounted } from "vue"
import { useRouter } from "vue-router"
import { useUserStore } from "@/stores/user"
import { useProfileStore } from "@/stores/profile"

const userStore = useUserStore()
userStore.init()

const profileStore = useProfileStore()

onMounted(() => {
  profileStore.fetchProfile()
})

const router = useRouter()
</script>

<template>
  <div id="app-root">
    <el-menu mode="horizontal" :ellipsis="false" :default-active="router.currentRoute.value.path" router>
      <el-menu-item index="/chat">
        <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" style="margin-right: 6px;">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
        </svg>
        对话
      </el-menu-item>
      <div class="spacer" />
      <el-menu-item v-if="profileStore.profile?.role === 'admin'" index="/admin/users">
        <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" style="margin-right: 6px;">
          <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
        </svg>
        用户管理
      </el-menu-item>
      <el-menu-item index="/">
        <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" style="margin-right: 6px;">
          <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" />
        </svg>
        我的
      </el-menu-item>
    </el-menu>
    <router-view />
  </div>
</template>

<style>
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}
#app, #app-root {
  min-height: 100vh;
}
.spacer {
  flex: 1;
}
</style>
