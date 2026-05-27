<script setup lang="ts">
import { onMounted, computed, ref } from "vue"
import { useRouter } from "vue-router"
import { useUserStore } from "@/stores/user"
import { useChatStore, type ChatSession } from "@/stores/chat"
import { useProfileStore, type UserProfile } from "@/stores/profile"
import { useFingerprint } from "@/composables/useFingerprint"
import { ElMessage } from "element-plus"

const router = useRouter()
const store = useUserStore()
const chatStore = useChatStore()
const profileStore = useProfileStore()
const { getDeviceId } = useFingerprint()

const editDialogVisible = ref(false)
const editForm = ref({
  username: "",
  email: "",
  phone: "",
  bio: "",
})

onMounted(async () => {
  if (!store.initialized) {
    await store.init()
  }
  await Promise.all([chatStore.fetchSessions(), profileStore.fetchProfile()])
})

const totalMessages = computed(() =>
  chatStore.sessions.reduce((sum: number, s: ChatSession) => sum + s.message_count, 0),
)

const daysActive = computed(() => {
  if (!store.userInfo?.first_seen) return 0
  const first = new Date(store.userInfo.first_seen)
  const now = new Date()
  return Math.max(1, Math.floor((now.getTime() - first.getTime()) / 86400000))
})

function openEditDialog() {
  const p = profileStore.profile
  editForm.value = {
    username: p?.username || "",
    email: p?.email || "",
    phone: p?.phone || "",
    bio: p?.bio || "",
  }
  editDialogVisible.value = true
}

async function saveProfile() {
  try {
    await profileStore.updateProfile({
      username: editForm.value.username || null,
      email: editForm.value.email || null,
      phone: editForm.value.phone || null,
      bio: editForm.value.bio || null,
    })
    editDialogVisible.value = false
    ElMessage.success("资料已保存")
  } catch {
    ElMessage.error("保存失败")
  }
}
</script>

<template>
  <div class="profile">
    <!-- Profile header -->
    <div class="profile-header">
      <div class="avatar">{{ (store.userInfo?.fingerprint || "U").slice(-2).toUpperCase() }}</div>
      <div class="profile-meta">
        <h2>{{ profileStore.profile?.username || "我的设备" }}</h2>
        <div class="device-id">{{ store.userInfo?.fingerprint || "加载中..." }}</div>
        <div class="member-since" v-if="store.userInfo?.first_seen">
          加入时间：{{ new Date(store.userInfo.first_seen).toLocaleDateString() }}
        </div>
      </div>
    </div>

    <div v-if="!store.userInfo" class="loading-state">
      <p>加载中...</p>
    </div>

    <template v-else>
      <!-- Stats cards -->
      <div class="stats-grid">
        <el-card shadow="never" class="stat-card" @click="router.push('/chat')" style="cursor: pointer;">
          <div class="stat-value">{{ chatStore.sessions.length }}</div>
          <div class="stat-label">总对话</div>
        </el-card>
        <el-card shadow="never" class="stat-card">
          <div class="stat-value">{{ totalMessages }}</div>
          <div class="stat-label">总消息</div>
        </el-card>
        <el-card shadow="never" class="stat-card">
          <div class="stat-value">{{ store.userInfo.visit_count }}</div>
          <div class="stat-label">访问次数</div>
        </el-card>
        <el-card shadow="never" class="stat-card">
          <div class="stat-value">{{ daysActive }}</div>
          <div class="stat-label">使用天数</div>
        </el-card>
      </div>

      <!-- Profile info card -->
      <el-card shadow="never" class="section-card">
        <template #header>
          <div class="section-header">
            <span>个人资料</span>
            <el-button text type="primary" size="small" @click="openEditDialog">
              编辑
            </el-button>
          </div>
        </template>
        <div class="profile-fields">
          <div class="field-row">
            <span class="field-label">用户名</span>
            <span class="field-value">{{ profileStore.profile?.username || "未设置" }}</span>
          </div>
          <div class="field-row">
            <span class="field-label">邮箱</span>
            <span class="field-value">{{ profileStore.profile?.email || "未设置" }}</span>
          </div>
          <div class="field-row">
            <span class="field-label">手机</span>
            <span class="field-value">{{ profileStore.profile?.phone || "未设置" }}</span>
          </div>
          <div class="field-row">
            <span class="field-label">简介</span>
            <span class="field-value">{{ profileStore.profile?.bio || "未设置" }}</span>
          </div>
        </div>
      </el-card>

      <!-- Recent sessions -->
      <el-card shadow="never" class="section-card">
        <template #header>
          <div class="section-header">
            <span>最近对话</span>
            <el-button text type="primary" size="small" @click="router.push('/chat')">
              查看全部
            </el-button>
          </div>
        </template>
        <div v-if="chatStore.sessions.length === 0" class="empty-hint">
          还没有对话，<el-link type="primary" @click="router.push('/chat')">开始第一个对话</el-link>
        </div>
        <div
          v-for="s in chatStore.sessions.slice(0, 5)"
          :key="s.id"
          class="session-row"
          @click="router.push('/chat')"
        >
          <div class="session-info">
            <div class="session-title">{{ s.title }}</div>
            <div class="session-meta">{{ s.message_count }} 条消息 · {{ new Date(s.updated_at).toLocaleDateString() }}</div>
          </div>
          <el-tag size="small" type="info">{{ s.message_count }}</el-tag>
        </div>
      </el-card>

      <!-- Actions -->
      <div class="actions">
        <el-button size="small" plain @click="store.fetchUserInfo(); chatStore.fetchSessions(); profileStore.fetchProfile()">刷新</el-button>
      </div>
    </template>

    <!-- Edit profile dialog -->
    <el-dialog v-model="editDialogVisible" title="编辑个人资料" width="420px" :close-on-click-modal="false">
      <el-form :model="editForm" label-width="60px">
        <el-form-item label="用户名">
          <el-input v-model="editForm.username" placeholder="请输入用户名" maxlength="50" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="editForm.email" placeholder="请输入邮箱" maxlength="100" />
        </el-form-item>
        <el-form-item label="手机">
          <el-input v-model="editForm.phone" placeholder="请输入手机号" maxlength="20" />
        </el-form-item>
        <el-form-item label="简介">
          <el-input v-model="editForm.bio" type="textarea" :rows="3" placeholder="写一句话介绍自己" maxlength="200" show-word-limit />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="profileStore.loading" @click="saveProfile">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.profile {
  max-width: 640px;
  margin: 0 auto;
  padding: 32px 20px;
}

/* Profile header */
.profile-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 28px;
}
.avatar {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: linear-gradient(135deg, #409eff, #337ecc);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  font-weight: 600;
  flex-shrink: 0;
}
.profile-meta h2 {
  margin: 0 0 4px;
  font-size: 20px;
}
.device-id {
  font-size: 12px;
  color: #909399;
  word-break: break-all;
  margin-bottom: 2px;
}
.member-since {
  font-size: 12px;
  color: #c0c4cc;
}

/* Stats */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 24px;
}
.stat-card {
  text-align: center;
  border-radius: 8px;
}
.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #303133;
}
.stat-label {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

/* Section card */
.section-card {
  margin-bottom: 24px;
  border-radius: 8px;
}
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* Profile fields */
.profile-fields {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.field-row {
  display: flex;
  align-items: center;
  padding: 4px 0;
}
.field-label {
  width: 60px;
  font-size: 13px;
  color: #909399;
  flex-shrink: 0;
}
.field-value {
  font-size: 14px;
  color: #303133;
}

/* Session rows */
.session-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 0;
  cursor: pointer;
  border-bottom: 1px solid #f0f0f0;
}
.session-row:last-child {
  border-bottom: none;
}
.session-info {
  flex: 1;
  min-width: 0;
}
.session-title {
  font-size: 14px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.session-meta {
  font-size: 12px;
  color: #c0c4cc;
  margin-top: 2px;
}
.empty-hint {
  text-align: center;
  padding: 24px 0;
  color: #909399;
  font-size: 14px;
}

/* Actions */
.actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.loading-state {
  text-align: center;
  padding: 60px 0;
  color: #909399;
}
</style>
