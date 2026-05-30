from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.session import engine
from app.middleware.fingerprint import FingerprintMiddleware
from app.routers import users
from app.routers import chat as chat_router
from app.routers import profiles
from app.config import settings


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
