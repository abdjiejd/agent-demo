const STORAGE_KEY = `${import.meta.env.VITE_PROJECT_NAME || "default"}_device_id`

// 简化版设备指纹：合并多个浏览器特征生成哈希
function generateFingerprint(): string {
  const canvas = document.createElement("canvas")
  canvas.width = 200
  canvas.height = 50
  const ctx = canvas.getContext("2d")
  if (ctx) {
    ctx.textBaseline = "top"
    ctx.font = "14px Arial"
    ctx.fillStyle = "#f60"
    ctx.fillRect(125, 1, 62, 20)
    ctx.fillStyle = "#069"
    ctx.fillText(import.meta.env.VITE_PROJECT_NAME || "Chat Demo", 2, 15)
    ctx.fillStyle = "rgba(102, 204, 0, 0.7)"
    ctx.fillText("fingerprint", 4, 17)
  }
  const canvasHash = canvas.toDataURL()

  const components = [
    canvasHash,
    screen.width,
    screen.height,
    screen.colorDepth,
    navigator.language,
    navigator.platform,
    navigator.userAgent,
    new Date().getTimezoneOffset(),
  ]

  const raw = components.join("|||")
  // 简单哈希
  let hash = 0
  for (let i = 0; i < raw.length; i++) {
    const char = raw.charCodeAt(i)
    hash = ((hash << 5) - hash) + char
    hash |= 0
  }
  return "fp_" + Math.abs(hash).toString(36) + Date.now().toString(36)
}

let cachedFingerprint: string | null = null

export function useFingerprint() {
  function getDeviceId(): string {
    if (cachedFingerprint) return cachedFingerprint

    let id = localStorage.getItem(STORAGE_KEY)
    if (!id) {
      id = generateFingerprint()
      localStorage.setItem(STORAGE_KEY, id)
    }
    cachedFingerprint = id
    return id
  }

  function resetDeviceId(): string {
    cachedFingerprint = null
    localStorage.removeItem(STORAGE_KEY)
    return getDeviceId()
  }

  return { getDeviceId, resetDeviceId }
}
