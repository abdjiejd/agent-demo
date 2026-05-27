<script setup lang="ts">
import { ref } from "vue"
import { useChatStore } from "@/stores/chat"

const chatStore = useChatStore()
const text = ref("")

function handleSend() {
  const content = text.value.trim()
  if (!content || chatStore.sending || !chatStore.currentSessionId) return
  chatStore.sendMessage(chatStore.currentSessionId, content)
  text.value = ""
}

function onKeydown(e: KeyboardEvent) {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault()
    handleSend()
  }
}
</script>

<template>
  <div class="chat-input">
    <div class="input-wrapper">
      <textarea
        v-model="text"
        placeholder="输入消息... (Enter 发送, Shift+Enter 换行)"
        :disabled="!chatStore.currentSessionId"
        rows="1"
        @keydown="onKeydown"
      />
      <el-button
        type="primary"
        :loading="chatStore.sending"
        :disabled="chatStore.sending || !text.trim() || !chatStore.currentSessionId"
        circle
        @click="handleSend"
      >
        <template #icon>
          <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5">
            <line x1="22" y1="2" x2="11" y2="13" />
            <polygon points="22 2 15 22 11 13 2 9 22 2" />
          </svg>
        </template>
      </el-button>
    </div>
  </div>
</template>

<style scoped>
.chat-input {
  border-top: 1px solid #e4e7ed;
  padding: 12px 20px;
  background: #fafafa;
}
.input-wrapper {
  display: flex;
  gap: 10px;
  align-items: flex-end;
}
textarea {
  flex: 1;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  padding: 10px 14px;
  font-size: 14px;
  font-family: inherit;
  resize: none;
  outline: none;
  line-height: 1.5;
  max-height: 150px;
  min-height: 42px;
  transition: border-color 0.2s;
}
textarea:focus {
  border-color: #409eff;
}
textarea:disabled {
  background: #f5f7fa;
  cursor: not-allowed;
}
</style>
