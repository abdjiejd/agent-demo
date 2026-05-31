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
  const initializing = ref(false)

  async function init(): Promise<boolean> {
    if (initialized.value || initializing.value) return true
    initializing.value = true
    try {
      const { getDeviceId } = useFingerprint()
      deviceId.value = getDeviceId()
      const ok = await fetchUserInfo()
      if (ok) initialized.value = true
      return ok
    } finally {
      initializing.value = false
    }
  }

  async function fetchUserInfo(): Promise<boolean> {
    loading.value = true
    try {
      const res = await apiClient.get("/users/me")
      userInfo.value = res.data as UserInfo
      return true
    } catch (e) {
      console.error("获取用户信息失败:", e)
      return false
    } finally {
      loading.value = false
    }
  }

  return { deviceId, userInfo, loading, initialized, initializing, init, fetchUserInfo }
})
