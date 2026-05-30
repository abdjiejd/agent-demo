import { defineStore } from "pinia"
import { ref, computed } from "vue"
import apiClient from "@/api/client"
import { useFingerprint } from "@/composables/useFingerprint"

export interface ChatSession {
  id: string
  title: string
  created_at: string
  updated_at: string
  message_count: number
}

export interface ChatMessage {
  id: number
  session_id: string
  role: string
  content: string
  created_at: string
}

export const useChatStore = defineStore("chat", () => {
  const sessions = ref<ChatSession[]>([])
  const currentSessionId = ref<string | null>(null)
  const messages = ref<ChatMessage[]>([])
  const sending = ref(false)
  const streamingMessage = ref("")
  const sessionsLoading = ref(false)
  const messagesLoading = ref(false)

  const currentSession = computed(() =>
    sessions.value.find((s) => s.id === currentSessionId.value) || null,
  )

  async function fetchSessions() {
    sessionsLoading.value = true
    try {
      const res = await apiClient.get<ChatSession[]>("/chat/sessions")
      sessions.value = res.data
    } catch (e) {
      console.error("获取会话列表失败:", e)
    } finally {
      sessionsLoading.value = false
    }
  }

  async function createSession(): Promise<string> {
    const res = await apiClient.post<ChatSession>("/chat/sessions", { title: "New Chat" })
    sessions.value.unshift(res.data)
    return res.data.id
  }

  async function renameSession(id: string, title: string) {
    await apiClient.patch(`/chat/sessions/${id}`, { title })
    const s = sessions.value.find((s) => s.id === id)
    if (s) s.title = title
  }

  async function deleteSession(id: string) {
    await apiClient.delete(`/chat/sessions/${id}`)
    sessions.value = sessions.value.filter((s) => s.id !== id)
    if (currentSessionId.value === id) {
      currentSessionId.value = null
      messages.value = []
    }
  }

  async function switchSession(id: string) {
    if (currentSessionId.value === id) return
    currentSessionId.value = id
    await fetchMessages(id)
  }

  async function fetchMessages(sessionId: string) {
    messagesLoading.value = true
    try {
      const res = await apiClient.get<ChatMessage[]>(`/chat/sessions/${sessionId}/messages`)
      messages.value = res.data
    } catch (e) {
      console.error("获取消息失败:", e)
    } finally {
      messagesLoading.value = false
    }
  }

  async function sendMessage(sessionId: string, content: string) {
    if (sending.value) return
    sending.value = true
    streamingMessage.value = ""

    // Optimistic user message
    const tempMsg: ChatMessage = {
      id: -Date.now(),
      session_id: sessionId,
      role: "user",
      content,
      created_at: new Date().toISOString(),
    }
    messages.value.push(tempMsg)

    const { getDeviceId } = useFingerprint()
    const deviceId = getDeviceId()

    try {
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL || "http://localhost:8082/api"}/chat/sessions/${sessionId}/messages`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Device-Id": deviceId,
        },
        body: JSON.stringify({ content }),
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }

      const reader = response.body!.getReader()
      const decoder = new TextDecoder()
      let buffer = ""

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split("\n")
        buffer = lines.pop() || ""

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue
          const raw = line.slice(6).trim()
          if (raw === "[DONE]") continue

          try {
            const event = JSON.parse(raw)
            if (event.type === "chunk") {
              streamingMessage.value += event.content
            } else if (event.type === "done") {
              messages.value.push({
                id: event.message_id,
                session_id: sessionId,
                role: "assistant",
                content: streamingMessage.value,
                created_at: new Date().toISOString(),
              })
              streamingMessage.value = ""
              // Refresh sessions to update message_count and title
              await fetchSessions()
            } else if (event.type === "error") {
              console.error("Stream error:", event.content)
              streamingMessage.value = `错误: ${event.content}`
            }
          } catch {
            // skip non-JSON data lines
          }
        }
      }
    } catch (e) {
      console.error("发送消息失败:", e)
      streamingMessage.value = `发送失败: ${e}`
    } finally {
      sending.value = false
    }
  }

  return {
    sessions,
    currentSessionId,
    currentSession,
    messages,
    sending,
    streamingMessage,
    sessionsLoading,
    messagesLoading,
    fetchSessions,
    createSession,
    renameSession,
    deleteSession,
    switchSession,
    fetchMessages,
    sendMessage,
  }
})
