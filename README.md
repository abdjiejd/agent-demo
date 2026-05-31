# agent-demo

一个基于大语言模型的智能问答项目，支持免注册使用、多会话管理和上下文对话，方便进行二次开发和功能扩展。

## 技术栈

- **后端**: Python FastAPI + SQLAlchemy (async) + MySQL
- **前端**: Vue 3 + TypeScript + Element Plus + Pinia + Vite
- **LLM**: 火山引擎 Ark API

## 已实现功能

### 💬 多会话管理
- 支持创建多个独立会话，会话之间互不干扰
- 会话列表按更新时间排序，显示消息数量
- 支持会话标题重命名和删除
- 自动根据首条消息内容生成会话标题

### 🔒 免登录自动识别（区别不同用户）
- 基于浏览器设备指纹（`X-Device-Id`）自动区分不同用户，无需注册登录
- 同一浏览器的用户自动关联其所有会话和历史消息，刷新页面后数据不丢失
- 不同设备/浏览器的用户之间完全隔离，彼此看不到对方的会话和数据
- 记录用户的访问次数、IP 和 User-Agent

### 🧠 短期记忆 / 上下文对话
- 每次对话携带最近 5 轮（10 条）消息作为上下文
- 大模型根据历史消息进行连贯回复
- 支持 SSE（Server-Sent Events）流式输出，实现打字机效果

### 🎨 对话界面
- Markdown 渲染与代码高亮（支持语法高亮）
- 消息气泡展示，用户和 AI 消息区分显示
- 响应式布局，支持移动端访问

### 👤 用户资料管理
- 可选填写昵称、邮箱、手机号、头像、个人简介
- 设备指纹与用户资料一一对应

## 项目结构

```
├── backend/                # FastAPI 后端
│   ├── app/
│   │   ├── main.py         # 应用入口
│   │   ├── config.py       # 配置读取
│   │   ├── database/
│   │   │   ├── session.py  # 数据库连接
│   │   │   └── models.py   # ORM 模型（匿名用户、会话、消息、用户资料）
│   │   ├── middleware/
│   │   │   └── fingerprint.py  # 设备指纹中间件
│   │   ├── routers/        # API 路由
│   │   │   ├── chat.py     # 会话和消息 CRUD + 流式对话
│   │   │   ├── users.py    # 用户相关
│   │   │   └── profiles.py # 用户资料管理
│   │   └── services/
│   │       └── llm.py      # 大模型调用（火山引擎 Ark API）
│   └── requirements.txt
├── frontend/               # Vue 3 前端
│   ├── src/
│   │   ├── api/            # API 客户端
│   │   ├── components/chat/ # 对话组件（会话列表、消息列表、输入框）
│   │   ├── composables/    # 组合式函数
│   │   ├── router/         # 路由配置
│   │   ├── stores/         # Pinia 状态管理（user、chat、profile）
│   │   └── views/          # 页面组件（Home、Chat）
│   └── package.json
├── sql/                    # 数据库脚本
└── README.md
```

## 快速开始

1. 复制 [INIT.example.md](INIT.example.md) 为 `INIT.md`
2. 填入你的数据库和大模型配置
3. 对 AI 说"按 INIT.md 初始化项目"

## 启动命令

### 后端
```bash
cd backend
venv\Scripts\uvicorn app.main:app --host 0.0.0.0 --port 8082 --reload
```

### 前端
```bash
cd frontend
npm run dev
```
