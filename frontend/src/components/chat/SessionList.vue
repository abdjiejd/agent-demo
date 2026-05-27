<script setup lang="ts">
import { ref, onMounted, onUnmounted } from "vue"
import { useChatStore } from "@/stores/chat"

const chatStore = useChatStore()
const editingId = ref<string | null>(null)
const editText = ref("")
const editInputRef = ref<HTMLInputElement | null>(null)

onMounted(() => document.addEventListener("click", clearEditing))
onUnmounted(() => document.removeEventListener("click", clearEditing))

let clearTimer: ReturnType<typeof setTimeout>
function clearEditing() {
  clearTimeout(clearTimer)
  clearTimer = setTimeout(() => { editingId.value = null }, 0)
}

async function handleCreate() {
  const id = await chatStore.createSession()
  await chatStore.switchSession(id)
}

async function handleDelete(id: string) {
  await chatStore.deleteSession(id)
}

function startEdit(session: { id: string; title: string }) {
  editingId.value = session.id
  editText.value = session.title
  setTimeout(() => editInputRef.value?.focus(), 50)
}

async function confirmEdit() {
  const id = editingId.value
  const title = editText.value.trim()
  editingId.value = null
  if (!id || !title) return
  await chatStore.renameSession(id, title)
}

function cancelEdit() {
  editingId.value = null
}
</script>

<template>
  <div class="session-list">
    <div class="session-header">
      <span class="title">会话</span>
      <el-button type="primary" size="small" circle @click="handleCreate">
        <template #icon>
          <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5">
            <line x1="12" y1="5" x2="12" y2="19" />
            <line x1="5" y1="12" x2="19" y2="12" />
          </svg>
        </template>
      </el-button>
    </div>

    <div v-loading="chatStore.sessionsLoading" class="session-items">
      <div
        v-for="session in chatStore.sessions"
        :key="session.id"
        class="session-item"
        :class="{ active: session.id === chatStore.currentSessionId }"
        @click="chatStore.switchSession(session.id)"
      >
        <!-- Editing state -->
        <template v-if="editingId === session.id">
          <input
            ref="editInputRef"
            v-model="editText"
            class="edit-input"
            @click.stop
            @keydown.enter="confirmEdit"
            @keydown.escape="cancelEdit"
          />
          <el-button class="action-btn" size="small" type="primary" link @click.stop="confirmEdit">
            <svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2.5">
              <polyline points="20 6 9 17 4 12" />
            </svg>
          </el-button>
          <el-button class="action-btn" size="small" type="info" link @click.stop="cancelEdit">
            <svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2.5">
              <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </el-button>
        </template>
        <!-- Display state -->
        <div v-else class="session-title" @dblclick.stop="startEdit(session)">
          {{ session.title }}
        </div>

        <el-button
          v-if="editingId !== session.id"
          class="action-btn"
          size="small"
          type="info"
          link
          @click.stop="startEdit(session)"
        >
          <svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
          </svg>
        </el-button>
        <el-button
          v-if="editingId !== session.id"
          class="action-btn delete-btn"
          size="small"
          type="danger"
          link
          @click.stop="handleDelete(session.id)"
        >
          <svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="3 6 5 6 21 6" />
            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
          </svg>
        </el-button>
      </div>

      <div v-if="chatStore.sessions.length === 0 && !chatStore.sessionsLoading" class="empty">
        暂无会话
      </div>
    </div>
  </div>
</template>

<style scoped>
.session-list {
  width: 260px;
  min-width: 260px;
  background: #f5f7fa;
  border-right: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
  height: 100%;
}
.session-header {
  padding: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #e4e7ed;
}
.session-header .title {
  font-weight: 600;
  font-size: 15px;
}
.session-items {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}
.session-item {
  display: flex;
  align-items: center;
  gap: 1px;
  padding: 10px 8px;
  border-radius: 6px;
  cursor: pointer;
  margin-bottom: 4px;
  transition: background 0.15s;
}
.session-item:hover {
  background: #e8eaed;
}
.session-item.active {
  background: #d9e2f7;
}
.session-title {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 14px;
  flex: 1;
  min-width: 0;
}
.edit-input {
  flex: 1;
  min-width: 0;
  border: 1px solid #409eff;
  border-radius: 4px;
  padding: 4px 6px;
  font-size: 14px;
  font-family: inherit;
  outline: none;
  background: #fff;
}
.action-btn {
  opacity: 0;
  transition: opacity 0.15s;
  flex-shrink: 0;
  padding: 2px !important;
  min-width: auto !important;
  margin-left: 0 !important;
}
.session-item:hover .action-btn {
  opacity: 0.6;
}
.session-item:hover .action-btn:hover {
  opacity: 1;
}
.delete-btn:hover {
  opacity: 1 !important;
}
.empty {
  text-align: center;
  color: #909399;
  padding: 32px 0;
  font-size: 14px;
}
</style>
