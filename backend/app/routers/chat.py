import json
import uuid
from collections.abc import AsyncGenerator
from datetime import datetime, timezone

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import select, func as sa_func

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from app.database.session import AsyncSessionLocal
from app.database.models import ChatSession, ChatMessage
from app.services.llm import stream_chat_with_tools, SYSTEM_PROMPT

router = APIRouter(prefix="/api/chat", tags=["chat"])


# --- Pydantic schemas ---

class CreateSessionRequest(BaseModel):
    title: str = "New Chat"


class SendMessageRequest(BaseModel):
    content: str


class UpdateSessionRequest(BaseModel):
    title: str


class SessionOut(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0


class MessageOut(BaseModel):
    id: int
    session_id: str
    role: str
    content: str
    created_at: datetime


# --- Session endpoints ---

@router.get("/sessions")
async def list_sessions(request: Request):
    fingerprint = request.state.fingerprint
    async with AsyncSessionLocal() as db:
        # subquery for message count
        count_stmt = (
            select(ChatMessage.session_id, sa_func.count(ChatMessage.id).label("cnt"))
            .group_by(ChatMessage.session_id)
            .subquery()
        )
        stmt = (
            select(ChatSession, count_stmt.c.cnt)
            .outerjoin(count_stmt, ChatSession.id == count_stmt.c.session_id)
            .where(ChatSession.fingerprint == fingerprint)
            .order_by(ChatSession.updated_at.desc())
        )
        result = await db.execute(stmt)
        rows = result.all()
        return [
            SessionOut(
                id=row.ChatSession.id,
                title=row.ChatSession.title,
                created_at=row.ChatSession.created_at,
                updated_at=row.ChatSession.updated_at,
                message_count=row.cnt or 0,
            )
            for row in rows
        ]


@router.post("/sessions", status_code=201)
async def create_session(request: Request, body: CreateSessionRequest):
    fingerprint = request.state.fingerprint
    session_id = str(uuid.uuid4())
    async with AsyncSessionLocal() as db:
        now = datetime.now(timezone.utc)
        session = ChatSession(
            id=session_id,
            fingerprint=fingerprint,
            title=body.title,
            created_at=now,
            updated_at=now,
        )
        db.add(session)
        await db.commit()
        return SessionOut(
            id=session.id,
            title=session.title,
            created_at=session.created_at,
            updated_at=session.updated_at,
            message_count=0,
        )


@router.delete("/sessions/{session_id}", status_code=204)
async def delete_session(request: Request, session_id: str):
    fingerprint = request.state.fingerprint
    async with AsyncSessionLocal() as db:
        session = await db.get(ChatSession, session_id)
        if not session or session.fingerprint != fingerprint:
            raise HTTPException(status_code=404, detail="Session not found")
        await db.delete(session)
        await db.commit()


@router.patch("/sessions/{session_id}")
async def update_session(request: Request, session_id: str, body: UpdateSessionRequest):
    fingerprint = request.state.fingerprint
    async with AsyncSessionLocal() as db:
        session = await db.get(ChatSession, session_id)
        if not session or session.fingerprint != fingerprint:
            raise HTTPException(status_code=404, detail="Session not found")
        session.title = body.title
        session.updated_at = datetime.now(timezone.utc)
        await db.flush()
        result = SessionOut(
            id=session.id,
            title=session.title,
            created_at=session.created_at,
            updated_at=session.updated_at,
            message_count=0,
        )
        await db.commit()
        return result


# --- Message endpoints ---

@router.get("/sessions/{session_id}/messages")
async def list_messages(request: Request, session_id: str):
    fingerprint = request.state.fingerprint
    async with AsyncSessionLocal() as db:
        session = await db.get(ChatSession, session_id)
        if not session or session.fingerprint != fingerprint:
            raise HTTPException(status_code=404, detail="Session not found")
        stmt = (
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.asc())
        )
        result = await db.execute(stmt)
        messages = result.scalars().all()
        return [
            MessageOut(
                id=m.id,
                session_id=m.session_id,
                role=m.role,
                content=m.content,
                created_at=m.created_at,
            )
            for m in messages
        ]


def _db_messages_to_langchain(
    db_messages: list[ChatMessage],
) -> list:
    """Convert DB-stored ChatMessage rows to LangChain message objects.

    Tool-calling messages are not persisted to DB, so only user/assistant
    messages are converted here.
    """
    langchain_messages: list = [SystemMessage(content=SYSTEM_PROMPT)]
    for m in db_messages:
        if m.role == "user":
            langchain_messages.append(HumanMessage(content=m.content))
        elif m.role == "assistant":
            langchain_messages.append(AIMessage(content=m.content))
    return langchain_messages


@router.post("/sessions/{session_id}/messages")
async def send_message(request: Request, session_id: str, body: SendMessageRequest):
    fingerprint = request.state.fingerprint

    if not body.content.strip():
        raise HTTPException(status_code=400, detail="Message content is required")

    # Validate session ownership and save user message in one session
    async with AsyncSessionLocal() as db:
        session = await db.get(ChatSession, session_id)
        if not session or session.fingerprint != fingerprint:
            raise HTTPException(status_code=404, detail="Session not found")

        # Save user message
        user_msg = ChatMessage(session_id=session_id, role="user", content=body.content)
        db.add(user_msg)
        await db.flush()

        # Fetch recent 10 messages (5 rounds) for context
        history_stmt = (
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.desc())
            .limit(10)
        )
        history_result = await db.execute(history_stmt)
        history_messages = list(reversed(history_result.scalars().all()))

        # Auto-title from first user message
        if session.title == "New Chat":
            session.title = body.content[:50] + ("..." if len(body.content) > 50 else "")
            await db.flush()

        await db.commit()

    # Convert to LangChain messages
    llm_messages = _db_messages_to_langchain(history_messages)

    async def event_stream() -> AsyncGenerator[str, None]:
        full_response = ""
        try:
            async for chunk in stream_chat_with_tools(llm_messages):
                full_response += chunk
                yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"

            # Save assistant message in a new DB session
            if full_response.strip():
                async with AsyncSessionLocal() as save_db:
                    assistant_msg = ChatMessage(
                        session_id=session_id,
                        role="assistant",
                        content=full_response,
                    )
                    save_db.add(assistant_msg)
                    await save_db.commit()
                    yield f"data: {json.dumps({'type': 'done', 'message_id': assistant_msg.id})}\n\n"
            else:
                yield f"data: {json.dumps({'type': 'error', 'content': '模型返回了空响应'})}\n\n"

        except Exception as e:
            import traceback
            yield f"data: {json.dumps({'type': 'error', 'content': f'{e}\n{traceback.format_exc()}'})}\n\n"
        finally:
            yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
