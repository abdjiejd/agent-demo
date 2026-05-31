import { defineStore } from "pinia"
import { ref } from "vue"
import apiClient from "@/api/client"
import { useFingerprint } from "@/composables/useFingerprint"

interface UserInfo {
  fingerprint: string
  ip: string | null
  visit_count: number
  first_seen: string | null
  last_seen: string | null
}

export const useUserStore = defineStore("user", () => {
  const deviceId = ref("")
  const userInfo = ref<UserInfo | null>(null)
  const loading = ref(false)
  const initialized = ref(false)

  async function init() {
    const { getDeviceId } = useFingerprint()
    deviceId.value = getDeviceId()
    await fetchUserInfo()
    initialized.value = true
  }

  async function fetchUserInfo() {
    loading.value = true
    try {
      const res = await apiClient.get("/users/me")
      userInfo.value = res.data as UserInfo
    } catch (e) {
      console.error("获取用户信息失败:", e)
    } finally {
      loading.value = false
    }
  }

  return { deviceId, userInfo, loading, initialized, init, fetchUserInfo }
})
