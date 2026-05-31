import secrets

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.database.session import AsyncSessionLocal
from app.database.models import User


class FingerprintMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 跳过预检请求和接口文档路由
        if request.method == "OPTIONS" or request.url.path in ("/docs", "/openapi.json", "/redoc"):
            return await call_next(request)

        fingerprint = request.headers.get("X-Device-Id")
        if not fingerprint:
            return JSONResponse(
                status_code=401,
                content={"detail": "Missing X-Device-Id header"},
            )

        # 从数据库查找或创建用户
        async with AsyncSessionLocal() as db:
            user = await db.get(User, fingerprint)
            if user:
                user.visit_count = user.visit_count + 1
                user.ip = request.client.host if request.client else None
                user.user_agent = request.headers.get("User-Agent")
                await db.commit()
            else:
                try:
                    default_username = "用户" + secrets.token_hex(3)
                    user = User(
                        fingerprint=fingerprint,
                        ip=request.client.host if request.client else None,
                        user_agent=request.headers.get("User-Agent"),
                        visit_count=1,
                        username=default_username,
                    )
                    db.add(user)
                    await db.commit()
                except IntegrityError:
                    # 并发创建用户时可能发生主键冲突，回滚后重新查询
                    await db.rollback()
                    user = await db.get(User, fingerprint)
                    if user:
                        user.visit_count = user.visit_count + 1
                        user.ip = request.client.host if request.client else None
                        user.user_agent = request.headers.get("User-Agent")
                    await db.commit()

        # 注入指纹到请求状态
        request.state.fingerprint = fingerprint
        return await call_next(request)
