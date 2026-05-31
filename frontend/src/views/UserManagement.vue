<script setup lang="ts">
import { ref, onMounted } from "vue"
import { useProfileStore, type AdminUser } from "@/stores/profile"

const profileStore = useProfileStore()

const users = ref<AdminUser[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const editingUser = ref<AdminUser | null>(null)
const editForm = ref({
  username: "",
  email: "",
  phone: "",
  bio: "",
  role: "user",
})

async function loadUsers() {
  loading.value = true
  try {
    users.value = await profileStore.fetchAllUsers()
  } catch (e) {
    console.error("获取用户列表失败:", e)
  } finally {
    loading.value = false
  }
}

function openEdit(user: AdminUser) {
  editingUser.value = user
  editForm.value = {
    username: user.username || "",
    email: user.email || "",
    phone: user.phone || "",
    bio: user.bio || "",
    role: user.role,
  }
  dialogVisible.value = true
}

async function saveEdit() {
  if (!editingUser.value) return
  try {
    await profileStore.adminUpdateUser(editingUser.value.fingerprint, editForm.value)
    dialogVisible.value = false
    await loadUsers()
  } catch (e) {
    console.error("更新用户失败:", e)
  }
}

function truncateFp(fp: string) {
  if (fp.length > 16) return fp.slice(0, 16) + "..."
  return fp
}

onMounted(loadUsers)
</script>

<template>
  <div class="user-management">
    <h2>用户管理</h2>
    <el-table :data="users" v-loading="loading" stripe style="width: 100%">
      <el-table-column label="头像" width="70">
        <template #default="{ row }">
          <el-avatar size="small">{{ (row.username || row.fingerprint).charAt(0).toUpperCase() }}</el-avatar>
        </template>
      </el-table-column>
      <el-table-column prop="username" label="用户名" min-width="120" />
      <el-table-column label="指纹" min-width="180">
        <template #default="{ row }">
          <el-tooltip :content="row.fingerprint" placement="top">
            <span>{{ truncateFp(row.fingerprint) }}</span>
          </el-tooltip>
        </template>
      </el-table-column>
      <el-table-column prop="email" label="邮箱" min-width="160" />
      <el-table-column prop="phone" label="电话" width="130" />
      <el-table-column label="角色" width="90">
        <template #default="{ row }">
          <el-tag :type="row.role === 'admin' ? 'danger' : 'info'" size="small">
            {{ row.role }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="visit_count" label="访问" width="70" align="center" />
      <el-table-column label="操作" width="100" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" size="small" @click="openEdit(row)">编辑</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" title="编辑用户" width="450px">
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="用户名">
          <el-input v-model="editForm.username" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="editForm.email" />
        </el-form-item>
        <el-form-item label="电话">
          <el-input v-model="editForm.phone" />
        </el-form-item>
        <el-form-item label="简介">
          <el-input v-model="editForm.bio" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="editForm.role">
            <el-option label="user" value="user" />
            <el-option label="admin" value="admin" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveEdit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.user-management {
  max-width: 1100px;
  margin: 0 auto;
  padding: 24px;
}
h2 {
  margin-bottom: 20px;
}
</style>
