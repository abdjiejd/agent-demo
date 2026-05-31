import socket
import sys
from contextlib import asynccontextmanager

from app.config import settings


def _check_port_available():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.5)
    result = s.connect_ex(("127.0.0.1", settings.SERVER_PORT))
    s.close()
    if result == 0:
        sys.exit(f"[ERROR] Port {settings.SERVER_PORT} 已被占用，请先关闭占用该端口的进程后再启动")


_check_port_available()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.session import engine
from app.middleware.fingerprint import FingerprintMiddleware
from app.routers import users
from app.routers import chat as chat_router
from app.routers import profiles


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(title=settings.PROJECT_NAME, version="0.1.0", lifespan=lifespan)

# CORS - 允许前端开发服务器
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        f"http://localhost:{settings.FRONTEND_PORT}",
        f"http://127.0.0.1:{settings.FRONTEND_PORT}",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 指纹中间件
app.add_middleware(FingerprintMiddleware)

# 路由
app.include_router(users.router)
app.include_router(chat_router.router)
app.include_router(profiles.router)
