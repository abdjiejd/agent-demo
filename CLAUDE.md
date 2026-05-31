# agent-demo 项目规则

## 项目概述

基于 LLM 的智能问答项目，后端 FastAPI + 前端 Vue 3，使用火山引擎 Ark API。

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

## 端口占用

如果启动时端口被占用，说明服务已经在运行，前后端都有热重载，可以直接测试。

## 配置

- 数据库和 LLM 的连接信息在全局 CLAUDE.md 中
- 后端 `.env` 修改后会自动热重载，无需手动重启
- 修改 `requirements.txt` 后需手动 `pip install`，uvicorn 不会自动处理
