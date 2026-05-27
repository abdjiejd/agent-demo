from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Request
from pydantic import BaseModel

from sqlalchemy import select

from app.database.session import AsyncSessionLocal
from app.database.models import UserProfile

router = APIRouter(prefix="/api/profiles", tags=["profiles"])


class ProfileOut(BaseModel):
    id: int
    fingerprint: str
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


async def _get_or_create_profile(db: AsyncSessionLocal, fingerprint: str) -> UserProfile:  # type: ignore
    result = await db.execute(select(UserProfile).where(UserProfile.fingerprint == fingerprint))
    profile = result.scalar_one_or_none()
    if profile is None:
        profile = UserProfile(fingerprint=fingerprint)
        db.add(profile)
        await db.commit()
        await db.refresh(profile)
    return profile


@router.get("/me", response_model=ProfileOut)
async def get_my_profile(request: Request):
    fingerprint = request.state.fingerprint
    async with AsyncSessionLocal() as db:
        profile = await _get_or_create_profile(db, fingerprint)
        return profile


@router.put("/me", response_model=ProfileOut)
async def update_my_profile(request: Request, body: ProfileUpdate):
    fingerprint = request.state.fingerprint
    async with AsyncSessionLocal() as db:
        profile = await _get_or_create_profile(db, fingerprint)

        if body.username is not None:
            profile.username = body.username
        if body.email is not None:
            profile.email = body.email
        if body.phone is not None:
            profile.phone = body.phone
        if body.avatar is not None:
            profile.avatar = body.avatar
        if body.bio is not None:
            profile.bio = body.bio

        await db.commit()
        await db.refresh(profile)
        return profile
