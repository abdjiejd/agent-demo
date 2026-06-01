# agent-demo

一个基于大语言模型的**智能体模板项目**，支持工具调用、免登录设备指纹识别、多会话管理和 LLM 日志记录。采用 **AI 引导初始化**，只需填写配置文件即可快速启动，非常适合进行二次开发和功能扩展。

## 技术栈

- **后端**: Python FastAPI + SQLAlchemy (async) + MySQL
- **前端**: Vue 3 + TypeScript + Element Plus + Pinia + Vite
- **LLM**: OpenAI API 兼容接口（支持火山引擎、DeepSeek 等）

## 核心特性

### 🤖 智能体能力
- 支持工具调用（Tool Calling），大模型可调用外部工具函数
- 支持多轮工具调用循环（Tool Call Loop），完成复杂任务
- 可轻松扩展自定义工具

### 💬 多会话管理
- 支持创建多个独立会话，会话之间互不干扰

### 🎨 对话界面
- Markdown 渲染与代码高亮
- 消息气泡展示，用户和 AI 消息区分显示
- 响应式布局，支持移动端访问

### 🔒 免登录设备指纹识别
- 基于浏览器 Canvas 设备指纹自动区分用户，无需注册登录
- 首次访问自动生成默认用户名，用户可自行修改

### 👤 个人主页
- 查看对话统计（总对话数、总消息数、访问次数、使用天数）
- 支持编辑用户名、邮箱、手机号、个人简介

### 📋 LLM 日志记录
- 每次大模型调用自动记录完整请求/响应日志（含工具调用）
- 管理员后台可查看和检索日志

## 项目结构

```
├── backend/                # FastAPI 后端
│   ├── app/
│   │   ├── main.py         # 应用入口
│   │   ├── config.py       # 配置读取
│   │   ├── database/
│   │   │   ├── session.py  # 数据库连接
│   │   │   └── models.py   # ORM 模型（users、chat_sessions、chat_messages、llm_logs）
│   │   ├── middleware/
│   │   │   └── fingerprint.py  # 设备指纹中间件
│   │   ├── routers/        # API 路由
│   │   │   ├── chat.py     # 会话和消息 CRUD + 流式对话
│   │   │   ├── users.py    # 用户信息 + 管理员接口（日志、用户管理）
│   │   │   └── profiles.py # 用户资料管理
│   │   └── services/
│   │       ├── llm.py      # 大模型调用（支持工具调用）
│   │       ├── tools.py    # 工具函数定义
│   │       └── log_context.py # LLM 日志记录
│   └── requirements.txt
├── frontend/               # Vue 3 前端
│   ├── src/
│   │   ├── api/            # API 客户端
│   │   ├── components/chat/ # 对话组件（会话列表、消息列表、输入框）
│   │   ├── composables/    # 设备指纹
│   │   ├── router/         # 路由配置
│   │   ├── stores/         # Pinia 状态管理（user、chat、profile）
│   │   └── views/          # 页面（Home、Chat、LogsManagement、UserManagement）
│   └── package.json
├── sql/                    # 数据库建表脚本
├── INIT.md                 # 初始化配置
├── CLAUDE.md               # 项目规则
└── README.md
```

## AI 引导初始化（推荐）

本项目采用 **AI 引导初始化** 方式，不需要手动创建数据库、配置环境变量、安装依赖等繁琐步骤。

1. 复制 [INIT.example.md](INIT.example.md) 为 `INIT.md`
2. 填入你的数据库和大模型配置（8 个必填项，可以让AI填，但是填好之后，AI必须让用户检查，然后才能开始执行初始化）
3. 对 AI 说"**按 INIT.md 初始化项目**"

## 启动命令

### 后端
```bash
cd backend
venv\Scripts\uvicorn app.main:app --host 0.0.0.0 --port 8082 --reload --reload-include ".env"
```

### 前端
```bash
cd frontend
npm run dev
```
