from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.database.session import AsyncSessionLocal
from app.database.models import User

router = APIRouter(prefix="/api/profiles", tags=["profiles"])


class ProfileOut(BaseModel):
    fingerprint: str
    role: str = "user"
    username: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None
    bio: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProfileUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None
    bio: Optional[str] = None


@router.get("/me", response_model=ProfileOut)
async def get_my_profile(request: Request):
    fingerprint = request.state.fingerprint
    async with AsyncSessionLocal() as db:
        user = await db.get(User, fingerprint)
        return ProfileOut(
            fingerprint=user.fingerprint,
            role=user.role,
            username=user.username,
            email=user.email,
            phone=user.phone,
            avatar=user.avatar,
            bio=user.bio,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )


@router.put("/me", response_model=ProfileOut)
async def update_my_profile(request: Request, body: ProfileUpdate):
    fingerprint = request.state.fingerprint
    async with AsyncSessionLocal() as db:
        user = await db.get(User, fingerprint)

        if body.username is not None:
            user.username = body.username
        if body.email is not None:
            user.email = body.email
        if body.phone is not None:
            user.phone = body.phone
        if body.avatar is not None:
            user.avatar = body.avatar
        if body.bio is not None:
            user.bio = body.bio

        await db.commit()
        await db.refresh(user)
        return ProfileOut(
            fingerprint=user.fingerprint,
            role=user.role,
            username=user.username,
            email=user.email,
            phone=user.phone,
            avatar=user.avatar,
            bio=user.bio,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
