import { defineStore } from "pinia"
import { ref } from "vue"
import apiClient from "@/api/client"

export interface UserProfile {
  fingerprint: string
  role: string
  username: string | null
  email: string | null
  phone: string | null
  avatar: string | null
  bio: string | null
  created_at: string
  updated_at: string
}

export interface AdminUser {
  fingerprint: string
  ip: string | null
  visit_count: number
  role: string
  username: string | null
  email: string | null
  phone: string | null
  bio: string | null
  first_seen: string | null
  last_seen: string | null
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

  async function fetchAllUsers(): Promise<AdminUser[]> {
    const res = await apiClient.get<AdminUser[]>("/admin/users")
    return res.data
  }

  async function adminUpdateUser(fingerprint: string, data: Partial<AdminUser>) {
    await apiClient.put(`/admin/users/${fingerprint}`, data)
  }

  return { profile, loading, fetchProfile, updateProfile, fetchAllUsers, adminUpdateUser }
})
