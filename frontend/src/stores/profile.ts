import { defineStore } from "pinia"
import { ref } from "vue"
import apiClient from "@/api/client"

export interface UserProfile {
  id: number
  fingerprint: string
  username: string | null
  email: string | null
  phone: string | null
  avatar: string | null
  bio: string | null
  created_at: string
  updated_at: string
}

export const useProfileStore = defineStore("profile", () => {
  const profile = ref<UserProfile | null>(null)
  const loading = ref(false)

  async function fetchProfile() {
    loading.value = true
    try {
      const res = await apiClient.get<UserProfile>("/profiles/me")
      profile.value = res.data
    } catch (e) {
      console.error("获取用户资料失败:", e)
    } finally {
      loading.value = false
    }
  }

  async function updateProfile(data: Partial<UserProfile>) {
    loading.value = true
    try {
      const res = await apiClient.put<UserProfile>("/profiles/me", data)
      profile.value = res.data
    } catch (e) {
      console.error("更新用户资料失败:", e)
      throw e
    } finally {
      loading.value = false
    }
  }

  return { profile, loading, fetchProfile, updateProfile }
})
