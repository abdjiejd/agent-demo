import axios from "axios"
import { useFingerprint } from "@/composables/useFingerprint"

const apiClient = axios.create({
  baseURL: "/api",
  timeout: 30000,
  headers: { "Content-Type": "application/json" },
})

// 请求拦截器：自动注入 X-Device-Id
apiClient.interceptors.request.use((config) => {
  const { getDeviceId } = useFingerprint()
  const deviceId = getDeviceId()
  config.headers["X-Device-Id"] = deviceId
  return config
})

export default apiClient
