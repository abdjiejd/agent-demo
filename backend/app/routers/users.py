from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from sqlalchemy import select

from app.database.session import AsyncSessionLocal
from app.database.models import User

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
