# Chat Seed

一个基础的问答项目，方便进行二次开发和功能扩展。

## 技术栈

- **后端**: Python FastAPI + SQLAlchemy (async) + MySQL
- **前端**: Vue 3 + TypeScript + Element Plus + Pinia + Vite
- **LLM**: 火山引擎 Ark API

## 项目结构

```
├── backend/                # FastAPI 后端
│   ├── app/
│   │   ├── main.py         # 应用入口
│   │   ├── config.py       # 配置读取
│   │   ├── database/
│   │   │   ├── session.py  # 数据库连接
│   │   │   └── models.py   # ORM 模型
│   │   ├── middleware/
│   │   │   └── fingerprint.py  # 设备指纹中间件
│   │   ├── routers/        # API 路由
│   │   └── services/       # 业务逻辑
│   └── requirements.txt
├── frontend/               # Vue 3 前端
│   └── src/
│       ├── api/            # API 客户端
│       ├── composables/    # 组合式函数
│       ├── router/         # 路由配置
│       ├── stores/         # Pinia 状态管理
│       ├── views/          # 页面组件
│       └── components/     # 通用组件
├── sql/                    # 数据库脚本
└── README.md
```

## 快速开始

### 1. 数据库

创建 MySQL 数据库：

```sql
CREATE DATABASE IF NOT EXISTS chat_demo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

表结构在启动时自动创建，也可手动导入：

```bash
mysql -h your-host -u your-user -p chat_demo < sql/chat_demo_schema.sql
```

### 2. 后端

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 复制并修改配置
cp .env.example .env
# 编辑 .env 填入数据库和 API 密钥

uvicorn app.main:app --host 0.0.0.0 --port 8765 --reload
```

### 3. 前端

```bash
cd frontend
npm install
npm run dev
```

访问 `http://localhost:5173`

## 配置说明

后端配置通过环境变量或 `.env` 文件读取，参考 [backend/.env.example](backend/.env.example)。
