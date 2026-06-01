# 复制为 INIT.md，填入下方数据后对 AI 说"按 INIT.md 初始化项目"

> 共 8 个必填项，请完整填写，不要遗漏。

### ① 项目名称

| 配置项 | 你的值（替换本列） |
|---|---|
| PROJECT_NAME | `[ 填项目名称，如：agent-demo ]` |

### ② 数据库配置 (MySQL)

| 配置项 | 你的值（替换本列） |
|---|---|
| MYSQL_HOST | `[ 填数据库IP ]` |
| MYSQL_PORT | `[ 填端口，默认3306 ]` |
| MYSQL_USER | `[ 填用户名 ]` |
| MYSQL_PASSWORD | `[ 填密码 ]` |
| MYSQL_DATABASE | `[ 填数据库名 ]` |

### ③ 大模型配置 (兼容 OpenAI API 格式)

| 配置项 | 你的值（替换本列） |
|---|---|
| LLM_API_KEY | `[ 填API Key ]` |
| LLM_MODEL | `[ 填模型ID ]` |
| LLM_BASE_URL | `[ 填API地址 ]` |

---

> 以下内容用户无需关注，是给 AI 看的初始化引导。

## AI 初始化步骤

### 1. 创建数据库
连接 MySQL，执行建库和建表：
```
CREATE DATABASE IF NOT EXISTS <用户填的数据库名> CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE <用户填的数据库名>;
SOURCE sql/schema.sql;
```

### 2. 生成后端 .env
读取 backend/.env.example，将用户填写的配置写入 backend/.env，其他有默认值的字段无需写入：
```
PROJECT_NAME=<用户值>
MYSQL_HOST=<用户值>
MYSQL_PORT=<用户值>
MYSQL_USER=<用户值>
MYSQL_PASSWORD=<用户值>
MYSQL_DATABASE=<用户值>
LLM_API_KEY=<用户值>
LLM_MODEL=<用户值>
LLM_BASE_URL=<用户值>
```

### 3. 生成前端 .env
读取 frontend/.env.example，将用户填写的配置写入 frontend/.env，格式：
```
VITE_PROJECT_NAME=<用户值>
VITE_BACKEND_URL=http://localhost:8082/api
```

### 4. 启动后端
```
cd backend
python -m venv venv
venv\Scripts\pip install -r requirements.txt
venv\Scripts\uvicorn app.main:app --host 0.0.0.0 --port 8082 --reload --reload-include ".env"
```

### 5. 启动前端
```
cd frontend
npm install
npm run dev
```

### 6. 验证
后端: http://localhost:8082/docs
前端: http://localhost:8081

### 7. 关闭前后端
验证结束之后关闭前后端服务，提示用户项目初始化成功
