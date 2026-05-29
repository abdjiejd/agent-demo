from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.session import engine
from app.database.models import Base
from app.middleware.fingerprint import FingerprintMiddleware
from app.routers import users
from app.routers import chat as chat_router
from app.routers import profiles


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时创建表 (生产环境建议用 alembic 迁移)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(title="Chat Demo", version="0.1.0", lifespan=lifespan)

# CORS - 允许前端开发服务器
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8081", "http://127.0.0.1:8081"],
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
