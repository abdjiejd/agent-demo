from __future__ import annotations

import json
import logging
from collections.abc import AsyncIterator

from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.messages.tool import ToolCall
from langchain_openai import ChatOpenAI

from app.config import settings
from app.services.tools import get_tools, get_tool_by_name

logger = logging.getLogger(__name__)

_llm: ChatOpenAI | None = None

SYSTEM_PROMPT = (
    "你是一个有用的AI助手，请用中文回答用户的问题，你的回答要尽量简洁"
    ""
)


def _messages_to_dicts(messages: list) -> list[dict]:
    """Convert LangChain messages to OpenAI-compatible dicts for logging."""
    result = []
    for msg in messages:
        d: dict = {"role": msg.type, "content": msg.content or None}
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            d["tool_calls"] = [
                {
                    "id": tc.get("id", ""),
                    "type": "function",
                    "function": {
                        "name": tc["name"],
                        "arguments": tc["args"] if isinstance(tc["args"], str) else json.dumps(tc["args"], ensure_ascii=False),
                    },
                }
                for tc in msg.tool_calls
            ]
        if hasattr(msg, "tool_call_id") and msg.tool_call_id:
            d["tool_call_id"] = msg.tool_call_id
        result.append(d)
    return result


def _tools_to_dicts(tools) -> list[dict]:
    """Convert LangChain tools to OpenAI function format for logging."""
    result = []
    for t in tools:
        try:
            params = t.args_schema.model_json_schema()
        except Exception:
            params = {}
        result.append({
            "type": "function",
            "function": {
                "name": t.name,
                "description": t.description,
                "parameters": params,
            },
        })
    return result


def _log_request(messages: list, tools=None, round: int = 1):
    llm = _get_llm()
    body: dict = {
        "type": "request",
        "round": round,
        "model": llm.model_name,
        "messages": _messages_to_dicts(messages),
        "stream": True,
    }
    if tools:
        body["tools"] = _tools_to_dicts(tools)
        body["tool_choice"] = "auto"
    logger.info(json.dumps(body, ensure_ascii=False, indent=2))


def _log_response(content: str, tool_calls=None, round: int = 1):
    message: dict = {"role": "assistant", "content": content or None}
    if tool_calls:
        message["tool_calls"] = [
            {
                "id": tc["id"],
                "type": "function",
                "function": {
                    "name": tc["name"],
                    "arguments": tc["args"] if isinstance(tc["args"], str) else json.dumps(tc["args"], ensure_ascii=False),
                },
            }
            for tc in tool_calls
        ]
    body: dict = {
        "type": "response",
        "round": round,
        "model": _get_llm().model_name,
        "choices": [
            {
                "index": 0,
                "finish_reason": "tool_calls" if tool_calls else "stop",
                "message": message,
            }
        ],
    }
    logger.info(json.dumps(body, ensure_ascii=False, indent=2))


def _get_llm() -> ChatOpenAI:
    global _llm
    if _llm is None:
        _llm = ChatOpenAI(
            api_key=settings.ARK_API_KEY,
            base_url=settings.ARK_BASE_URL,
            model=settings.ARK_MODEL,
        )
    return _llm


async def stream_chat(messages: list) -> AsyncIterator[str]:
    """Simple streaming without tools."""
    llm = _get_llm()
    _log_request(messages)
    content_chunks: list[str] = []
    async for chunk in llm.astream(messages):
        if chunk.content:
            content_chunks.append(chunk.content)
            yield chunk.content
    _log_response("".join(content_chunks))


async def stream_chat_with_tools(
    messages: list,
) -> AsyncIterator[str]:
    """Stream a chat response with tool-calling support.

    Phase 1 streams the model response and collects tool_calls on the fly.
    If the model calls tools, they are executed and the loop continues.

    Phase 2 streams any final plain-text answer directly.

    Because Phase 1 is already streaming, every response path produces
    token-by-token output — no double API call needed.
    """
    llm = _get_llm()
    tools = get_tools()
    model_with_tools = llm.bind_tools(tools)
    max_rounds = settings.TOOL_CALL_MAX_ROUNDS

    for round_num in range(1, max_rounds + 1):
        # Collect content chunks and tool-call fragments from the stream
        content_chunks: list[str] = []
        tool_call_fragments: dict[int, dict[str, str]] = {}
        _log_request(messages, tools, round=round_num)

        try:
            async for chunk in model_with_tools.astream(messages):
                # Accumulate text content
                if chunk.content:
                    content_chunks.append(chunk.content)
                    yield chunk.content

                # Accumulate incremental tool-call data
                if chunk.tool_call_chunks:
                    for tcc in chunk.tool_call_chunks:
                        idx = tcc["index"]
                        if idx not in tool_call_fragments:
                            tool_call_fragments[idx] = {
                                "id": "",
                                "name": "",
                                "args": "",
                            }
                        frag = tool_call_fragments[idx]
                        if tcc.get("id"):
                            frag["id"] += tcc["id"]
                        if tcc.get("name"):
                            frag["name"] += tcc["name"]
                        if tcc.get("args"):
                            frag["args"] += tcc["args"]
        except Exception:
            logger.warning(
                "Tool calling not supported, falling back to plain streaming",
                exc_info=True,
            )
            async for chunk in llm.astream(messages):
                if chunk.content:
                    yield chunk.content
            return

        if not tool_call_fragments:
            # No tool calls — everything we just streamed is the final answer.
            # Reconstruct the AIMessage so it can be persisted to history.
            response = AIMessage(content="".join(content_chunks))
            messages.append(response)
            _log_response("".join(content_chunks), round=round_num)
            return

        # Reconstruct full tool calls from fragments
        tool_calls: list[ToolCall] = []
        for idx in sorted(tool_call_fragments):
            frag = tool_call_fragments[idx]
            tool_calls.append({
                "name": frag["name"],
                "args": json.loads(frag["args"]) if frag["args"] else {},
                "id": frag["id"] or f"call_{idx}",
                "type": "tool_call",
            })

        collected_content = "".join(content_chunks)
        _log_response(collected_content, tool_calls, round=round_num)
        response = AIMessage(content=collected_content, tool_calls=tool_calls)
        messages.append(response)

        for tc in tool_calls:
            tool_obj = get_tool_by_name(tc["name"])
            result = await tool_obj.ainvoke(tc["args"])
            result_str = (
                json.dumps(result, ensure_ascii=False)
                if not isinstance(result, str)
                else result
            )
            messages.append(ToolMessage(content=result_str, tool_call_id=tc["id"]))
