# agent-demo 项目规则

## 端口占用

如果启动时端口被占用，说明服务已经在运行，前后端都有热重载，可以直接测试,不需要重启

## 配置
- 后端 `.env` 修改后会自动热重载，无需手动重启
- 修改 `requirements.txt` 后需手动 `pip install`，uvicorn 不会自动处理
