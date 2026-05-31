from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from sqlalchemy import select

from app.database.session import AsyncSessionLocal
from app.database.models import AnonymousUser, UserProfile

router = APIRouter(prefix="/api/users", tags=["users"])
admin_router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/me")
async def get_current_user(request: Request):
    fingerprint = request.state.fingerprint
    async with AsyncSessionLocal() as db:
        user = await db.get(AnonymousUser, fingerprint)
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
        profile = await db.execute(
            select(UserProfile).where(UserProfile.fingerprint == fingerprint)
        )
        profile = profile.scalar_one_or_none()
        if not profile or profile.role != "admin":
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
        stmt = (
            select(AnonymousUser)
            .outerjoin(UserProfile)
            .order_by(AnonymousUser.last_seen.desc())
        )
        result = await db.execute(stmt)
        users = result.scalars().all()

        # Fetch profiles for these users
        fingerprints = [u.fingerprint for u in users]
        profile_stmt = select(UserProfile).where(UserProfile.fingerprint.in_(fingerprints))
        profile_result = await db.execute(profile_stmt)
        profiles = {p.fingerprint: p for p in profile_result.scalars().all()}

        output = []
        for u in users:
            p = profiles.get(u.fingerprint)
            output.append(AdminUserOut(
                fingerprint=u.fingerprint,
                ip=u.ip,
                visit_count=u.visit_count,
                role=p.role if p else "user",
                username=p.username if p else None,
                email=p.email if p else None,
                phone=p.phone if p else None,
                bio=p.bio if p else None,
                first_seen=u.first_seen.isoformat() if u.first_seen else None,
                last_seen=u.last_seen.isoformat() if u.last_seen else None,
            ))
        return output


@admin_router.put("/users/{fingerprint}")
async def update_user(fingerprint: str, body: AdminUserUpdate, request: Request):
    await _check_admin(request)
    async with AsyncSessionLocal() as db:
        user = await db.get(AnonymousUser, fingerprint)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")

        profile_result = await db.execute(
            select(UserProfile).where(UserProfile.fingerprint == fingerprint)
        )
        profile = profile_result.scalar_one_or_none()

        if body.role is not None:
            if profile:
                profile.role = body.role
        if body.username is not None:
            if profile:
                profile.username = body.username
        if body.email is not None:
            if profile:
                profile.email = body.email
        if body.phone is not None:
            if profile:
                profile.phone = body.phone
        if body.bio is not None:
            if profile:
                profile.bio = body.bio

        if profile:
            profile.updated_at = datetime.now()

        await db.commit()
        return {"message": "ok"}
