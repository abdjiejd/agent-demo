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
    "你是一个有用的AI助手，请用中文回答用户的问题。"
    "你可以使用提供的工具来获取实时信息，例如查询天气。"
    "当用户询问天气时，请使用 get_weather 工具查询后再回答。"
)


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
    async for chunk in llm.astream(messages):
        if chunk.content:
            yield chunk.content


async def stream_chat_with_tools(
    messages: list,
    max_tool_rounds: int = 5,
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

    for _ in range(max_tool_rounds):
        # Collect content chunks and tool-call fragments from the stream
        content_chunks: list[str] = []
        tool_call_fragments: dict[int, dict[str, str]] = {}

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
