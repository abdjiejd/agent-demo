<script setup lang="ts">
import { onMounted } from "vue"
import { useChatStore } from "@/stores/chat"
import SessionList from "@/components/chat/SessionList.vue"
import ChatMessages from "@/components/chat/ChatMessages.vue"
import ChatInput from "@/components/chat/ChatInput.vue"

const chatStore = useChatStore()

onMounted(async () => {
  await chatStore.fetchSessions()
  if (chatStore.sessions.length === 0) {
    const id = await chatStore.createSession()
    await chatStore.switchSession(id)
  } else {
    await chatStore.switchSession(chatStore.sessions[0].id)
  }
})
</script>

<template>
  <div class="chat-view">
    <SessionList />
    <div class="chat-main">
      <template v-if="chatStore.currentSessionId">
        <ChatMessages />
        <ChatInput />
      </template>
      <div v-else class="no-session">
        <p>请选择或创建一个会话</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.chat-view {
  display: flex;
  height: calc(100vh - 60px); /* subtract nav height */
  overflow: hidden;
}
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}
.no-session {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #909399;
}
</style>
