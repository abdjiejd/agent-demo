import { createRouter, createWebHistory } from "vue-router"
import Home from "@/views/Home.vue"
import Chat from "@/views/Chat.vue"
import UserManagement from "@/views/UserManagement.vue"

const routes = [
  { path: "/", name: "Home", component: Home },
  { path: "/chat", name: "Chat", component: Chat },
  { path: "/admin/users", name: "UserManagement", component: UserManagement },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
