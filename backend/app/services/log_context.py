from __future__ import annotations

import json
import logging
import uuid
from contextvars import ContextVar
from datetime import datetime
from typing import Any

from app.config import settings

logger = logging.getLogger(__name__)


class LogContext:
    def __init__(self, fingerprint: str, session_id: str, title: str):
        self.run_id = str(uuid.uuid4())
        self.fingerprint = fingerprint
        self.session_id = session_id
        self.title = title
        self.entries: list[dict[str, Any]] = []
        self.start_time = datetime.now()
        self.end_time: datetime | None = None
        self.error: str | None = None
        self._total_rounds: int = 0

    @property
    def total_rounds(self) -> int:
        return self._total_rounds

    @total_rounds.setter
    def total_rounds(self, value: int):
        self._total_rounds = max(self._total_rounds, value)


_context: ContextVar[LogContext | None] = ContextVar("log_context", default=None)


def start(fingerprint: str, session_id: str, title: str) -> LogContext | None:
    if not settings.LOG_LLM:
        return None
    ctx = LogContext(fingerprint, session_id, title)
    _context.set(ctx)
    return ctx


def append_entry(entry: dict[str, Any]):
    ctx = _context.get(None)
    if ctx is not None:
        ctx.entries.append(entry)


def set_rounds(rounds: int):
    ctx = _context.get(None)
    if ctx is not None:
        ctx.total_rounds = rounds


def set_error(error: str):
    ctx = _context.get(None)
    if ctx is not None:
        ctx.error = error


def _fmt_time(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%S.") + f"{dt.microsecond // 1000:03d}"


def finalize(error: str | None = None):
    ctx = _context.get(None)
    if ctx is None:
        return
    try:
        ctx.end_time = datetime.now()
        elapsed_ms = (ctx.end_time - ctx.start_time).total_seconds() * 1000
        output: dict[str, Any] = {
            "run_id": ctx.run_id,
            "fingerprint": ctx.fingerprint,
            "session_id": ctx.session_id,
            "title": ctx.title,
            "status": "error" if error else "ok",
            "entries": ctx.entries,
            "start_time": _fmt_time(ctx.start_time),
            "end_time": _fmt_time(ctx.end_time),
            "elapsed_ms": round(elapsed_ms, 2),
            "total_rounds": ctx.total_rounds,
            "error_msg": error,
        }
        logger.info(json.dumps(output, ensure_ascii=False, indent=2))
    finally:
        _context.set(None)
