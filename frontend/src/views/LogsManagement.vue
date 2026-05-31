<script setup lang="ts">
import { ref, onMounted } from "vue"
import { useProfileStore } from "@/stores/profile"
import apiClient from "@/api/client"

interface LogItem {
  id: number
  fingerprint: string | null
  username: string | null
  title: string | null
  created_at: string
}

interface LogDetail extends LogItem {
  data: string
}

const profileStore = useProfileStore()

const items = ref<LogItem[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const totalPages = ref(0)
const loading = ref(false)
const detailVisible = ref(false)
const detail = ref<LogDetail | null>(null)
const detailLoading = ref(false)

async function loadLogs() {
  loading.value = true
  try {
    const res = await apiClient.get("/admin/logs", {
      params: { page: page.value, page_size: pageSize.value },
    })
    items.value = res.data.items
    total.value = res.data.total
    page.value = res.data.page
    totalPages.value = res.data.total_pages
  } catch (e) {
    console.error("获取日志失败:", e)
  } finally {
    loading.value = false
  }
}

async function showDetail(log: LogItem) {
  detailLoading.value = true
  detailVisible.value = true
  try {
    const res = await apiClient.get<LogDetail>(`/admin/logs/${log.id}`)
    detail.value = res.data
  } catch (e) {
    console.error("获取日志详情失败:", e)
    detailVisible.value = false
  } finally {
    detailLoading.value = false
  }
}

function handlePageChange(p: number) {
  page.value = p
  loadLogs()
}

function formatJson(data: string): string {
  try {
    return JSON.stringify(JSON.parse(data), null, 2)
  } catch {
    return data
  }
}

onMounted(loadLogs)
</script>

<template>
  <div class="logs-management">
    <h2>日志</h2>
    <el-table :data="items" v-loading="loading" stripe style="width: 100%">
      <el-table-column prop="id" label="ID" width="70" align="center" />
      <el-table-column prop="username" label="用户" width="150" show-overflow-tooltip />
      <el-table-column prop="title" label="标题" min-width="200" show-overflow-tooltip />
      <el-table-column prop="created_at" label="时间" width="180" />
      <el-table-column label="操作" width="100" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" size="small" @click="showDetail(row)">查看</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination-wrapper" v-if="totalPages > 0">
      <el-pagination
        v-model:current-page="page"
        :page-size="pageSize"
        :total="total"
        layout="total, prev, pager, next"
        @current-change="handlePageChange"
      />
    </div>

    <el-dialog v-model="detailVisible" title="日志详情" width="800px" top="5vh">
      <template v-if="detail && !detailLoading">
        <div class="detail-meta">
          <span>ID: {{ detail.id }}</span>
          <span class="detail-sep">|</span>
          <span>用户: {{ detail.username || "未知" }}</span>
          <span class="detail-sep">|</span>
          <span>标题: {{ detail.title || "无" }}</span>
          <span class="detail-sep">|</span>
          <span>时间: {{ detail.created_at }}</span>
        </div>
        <el-input
          type="textarea"
          :model-value="formatJson(detail.data)"
          readonly
          :rows="20"
          class="detail-data"
        />
      </template>
      <div v-if="detailLoading" class="detail-loading">加载中...</div>
    </el-dialog>
  </div>
</template>

<style scoped>
.logs-management {
  max-width: 1100px;
  margin: 0 auto;
  padding: 24px;
}
h2 {
  margin-bottom: 20px;
}
.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}
.detail-meta {
  margin-bottom: 16px;
  font-size: 13px;
  color: #606266;
}
.detail-sep {
  margin: 0 10px;
  color: #dcdfe6;
}
.detail-loading {
  text-align: center;
  padding: 40px;
  color: #909399;
}
</style>
