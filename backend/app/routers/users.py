from datetime import datetime
from typing import Optional

from math import ceil

from fastapi import APIRouter, Request, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, func as sa_func

from app.database.session import AsyncSessionLocal
from app.database.models import User, LlmLog

router = APIRouter(prefix="/api/users", tags=["users"])
admin_router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/me")
async def get_current_user(request: Request):
    fingerprint = request.state.fingerprint
    async with AsyncSessionLocal() as db:
        user = await db.get(User, fingerprint)
        if user is None:
            return {"fingerprint": fingerprint, "is_new": True}
        return {
            "fingerprint": user.fingerprint,
            "ip": user.ip,
            "visit_count": user.visit_count,
            "first_seen": user.first_seen.isoformat() if user.first_seen else None,
            "last_seen": user.last_seen.isoformat() if user.last_seen else None,
        }


async def _check_admin(request: Request) -> str:
    fingerprint = request.state.fingerprint
    async with AsyncSessionLocal() as db:
        user = await db.get(User, fingerprint)
        if not user or user.role != "admin":
            raise HTTPException(status_code=403, detail="仅管理员可执行此操作")
        return fingerprint


class AdminUserOut(BaseModel):
    fingerprint: str
    ip: Optional[str] = None
    visit_count: int = 0
    role: str = "user"
    username: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    first_seen: Optional[str] = None
    last_seen: Optional[str] = None

    model_config = {"from_attributes": True}


class AdminUserUpdate(BaseModel):
    role: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None


@admin_router.get("/users")
async def list_users(request: Request):
    await _check_admin(request)
    async with AsyncSessionLocal() as db:
        stmt = select(User).order_by(User.last_seen.desc())
        result = await db.execute(stmt)
        users = result.scalars().all()
        return [AdminUserOut(
            fingerprint=u.fingerprint,
            ip=u.ip,
            visit_count=u.visit_count,
            role=u.role,
            username=u.username,
            email=u.email,
            phone=u.phone,
            bio=u.bio,
            first_seen=u.first_seen.isoformat() if u.first_seen else None,
            last_seen=u.last_seen.isoformat() if u.last_seen else None,
        ) for u in users]


@admin_router.put("/users/{fingerprint}")
async def update_user(fingerprint: str, body: AdminUserUpdate, request: Request):
    await _check_admin(request)
    async with AsyncSessionLocal() as db:
        user = await db.get(User, fingerprint)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")

        if body.role is not None:
            user.role = body.role
        if body.username is not None:
            user.username = body.username
        if body.email is not None:
            user.email = body.email
        if body.phone is not None:
            user.phone = body.phone
        if body.bio is not None:
            user.bio = body.bio

        user.updated_at = datetime.now()

        await db.commit()
        return {"message": "ok"}


class LogOut(BaseModel):
    id: int
    title: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class LogDetailOut(LogOut):
    data: str


@admin_router.get("/logs")
async def list_logs(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    await _check_admin(request)
    async with AsyncSessionLocal() as db:
        count_stmt = select(sa_func.count(LlmLog.id))
        total = (await db.execute(count_stmt)).scalar() or 0

        stmt = (
            select(LlmLog)
            .order_by(LlmLog.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await db.execute(stmt)
        logs = result.scalars().all()

        return {
            "items": [LogOut(id=log.id, title=log.title, created_at=log.created_at) for log in logs],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": ceil(total / page_size) if page_size else 0,
        }


@admin_router.get("/logs/{log_id}")
async def get_log_detail(log_id: int, request: Request):
    await _check_admin(request)
    async with AsyncSessionLocal() as db:
        log = await db.get(LlmLog, log_id)
        if not log:
            raise HTTPException(status_code=404, detail="日志不存在")
        return LogDetailOut(id=log.id, title=log.title, data=log.data, created_at=log.created_at)
