<script setup lang="ts">
import { nextTick, ref, watch } from "vue"
import { useChatStore } from "@/stores/chat"
import { renderMarkdown } from "@/utils/markdown"

const chatStore = useChatStore()
const containerRef = ref<HTMLElement | null>(null)

watch(
  () => [chatStore.messages.length, chatStore.streamingMessage],
  async () => {
    await nextTick()
    if (containerRef.value) {
      containerRef.value.scrollTop = containerRef.value.scrollHeight
    }
  },
  { deep: true },
)
</script>

<template>
  <div ref="containerRef" class="chat-messages" v-loading="chatStore.messagesLoading">
    <div v-if="chatStore.messages.length === 0 && !chatStore.messagesLoading" class="empty-state">
      <svg viewBox="0 0 24 24" width="48" height="48" fill="none" stroke="#c0c4cc" stroke-width="1.5">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
      </svg>
      <p>开始一个新的对话</p>
    </div>

    <div v-for="msg in chatStore.messages" :key="msg.id" class="message-row" :class="msg.role">
      <div class="avatar-col">
        <div class="time">{{ new Date(msg.created_at).toLocaleTimeString() }}</div>
        <div class="avatar">
          <svg v-if="msg.role === 'assistant'" viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z" />
          </svg>
          <svg v-else viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
            <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" />
          </svg>
        </div>
      </div>
      <div class="bubble">
        <div class="content" v-html="renderMarkdown(msg.content)" />
      </div>
    </div>

    <!-- AI thinking (no content yet) -->
    <div v-if="chatStore.sending && !chatStore.streamingMessage" class="message-row assistant">
      <div class="avatar">
        <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z" />
        </svg>
      </div>
      <div class="bubble thinking">
        <span class="dot-pulse" />
        <span class="thinking-text">AI 正在思考</span>
      </div>
    </div>

    <!-- Streaming message -->
    <div v-if="chatStore.sending && chatStore.streamingMessage" class="message-row assistant">
      <div class="avatar">
        <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z" />
        </svg>
      </div>
      <div class="bubble streaming">
        <span v-text="chatStore.streamingMessage" />
        <span class="cursor" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px 28px;
  background: #fff;
}
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #c0c4cc;
}
.empty-state p {
  margin-top: 12px;
  font-size: 14px;
}
.message-row {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
  max-width: 78%;
}
.message-row.user {
  flex-direction: row-reverse;
  margin-left: auto;
}
.avatar-col {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  flex-shrink: 0;
}
.avatar {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.message-row.user .avatar {
  background: #409eff;
  color: #fff;
}
.message-row.assistant .avatar {
  background: #67c23a;
  color: #fff;
}
.time {
  font-size: 10px;
  color: #bbb;
  white-space: nowrap;
  letter-spacing: 0;
}
.bubble {
  background: #f0f2f5;
  border-radius: 14px;
  padding: 12px 18px;
  position: relative;
}
.message-row.user .bubble {
  background: #409eff;
  color: #fff;
}
.content {
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.4;
  font-size: 15px;
  letter-spacing: 0.02em;
}
.streaming {
  background: #f0f2f5 !important;
  color: #333 !important;
}
.thinking {
  background: #f0f2f5 !important;
  color: #909399 !important;
  display: flex;
  align-items: center;
  gap: 8px;
}
.thinking-text {
  font-size: 14px;
}
.dot-pulse {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #67c23a;
  animation: pulse 1.2s ease-in-out infinite;
}
@keyframes pulse {
  0%, 80%, 100% { opacity: 0.3; transform: scale(0.8); }
  40% { opacity: 1; transform: scale(1.1); }
}
.cursor {
  display: inline-block;
  width: 2px;
  height: 1em;
  background: #409eff;
  margin-left: 2px;
  vertical-align: text-bottom;
  animation: blink 0.8s step-end infinite;
}
@keyframes blink {
  50% { opacity: 0; }
}

/* Markdown rendered content */
.content :deep(p) {
  margin: 0 0 4px;
  line-height: 1.4;
  white-space: normal;
}
.content :deep(p:last-child) {
  margin-bottom: 0;
}
.content :deep(pre) {
  background: #f6f8fa;
  border-radius: 8px;
  padding: 12px;
  overflow-x: auto;
  margin: 8px 0;
  font-size: 13px;
  line-height: 1.45;
  white-space: pre;
}
.content :deep(code) {
  font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
  background: #f0f2f5;
  padding: 3px 7px;
  border-radius: 4px;
  font-size: 0.88em;
  letter-spacing: 0;
}
.content :deep(pre code) {
  background: none;
  padding: 0;
  border-radius: 0;
  font-size: inherit;
  letter-spacing: 0;
}
.content :deep(ul),
.content :deep(ol) {
  margin: 6px 0;
  padding-left: 22px;
}
.content :deep(li) {
  margin: 1px 0;
  line-height: 1.4;
  white-space: normal;
}
.content :deep(blockquote) {
  margin: 10px 0;
  padding: 6px 16px;
  border-left: 3px solid #409eff;
  color: #606266;
  background: #f8f9fa;
  border-radius: 0 6px 6px 0;
}
.content :deep(h1),
.content :deep(h2),
.content :deep(h3),
.content :deep(h4) {
  margin: 16px 0 10px;
  font-weight: 600;
  letter-spacing: 0.02em;
}
.content :deep(h1) { font-size: 18px; }
.content :deep(h2) { font-size: 16px; }
.content :deep(h3) { font-size: 15px; }
.content :deep(h4) { font-size: 14px; }
.content :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 10px 0;
  font-size: 13.5px;
}
.content :deep(th),
.content :deep(td) {
  border: 1px solid #e0e0e0;
  padding: 8px 12px;
  text-align: left;
}
.content :deep(th) {
  background: #f5f7fa;
  font-weight: 600;
}
.content :deep(hr) {
  border: none;
  border-top: 1px solid #e4e7ed;
  margin: 16px 0;
}
.content :deep(a) {
  color: #409eff;
  text-decoration: none;
}
.content :deep(a:hover) {
  text-decoration: underline;
}
.content :deep(img) {
  max-width: 100%;
  border-radius: 6px;
  margin: 10px 0;
}
/* User bubble: override markdown colors for dark text on blue bg */
.message-row.user .content :deep(code) {
  background: rgba(255,255,255,0.2);
  color: #fff;
}
.message-row.user .content :deep(blockquote) {
  border-left-color: rgba(255,255,255,0.6);
  color: rgba(255,255,255,0.9);
  background: rgba(255,255,255,0.1);
}
.message-row.user .content :deep(a) {
  color: #b3d8ff;
}
.message-row.user .content :deep(pre) {
  background: rgba(0,0,0,0.15);
}
.message-row.user .content :deep(pre code) {
  background: none;
  color: #fff;
}
.message-row.user .content :deep(th) {
  background: rgba(255,255,255,0.15);
}
.message-row.user .content :deep(th),
.message-row.user .content :deep(td) {
  border-color: rgba(255,255,255,0.2);
}
</style>
