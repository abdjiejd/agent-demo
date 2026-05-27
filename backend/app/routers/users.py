from fastapi import APIRouter, Request

from app.database.session import AsyncSessionLocal
from app.database.models import AnonymousUser

router = APIRouter(prefix="/api/users", tags=["users"])


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
