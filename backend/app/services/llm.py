from __future__ import annotations

import json
import logging
from collections.abc import AsyncIterator

from langchain_core.messages import AIMessage, ToolMessage
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

    Phase 1 — non-streaming tool-calling loop:
        If the model decides to call tools, execute them and feed results back
        until the model returns a plain-text response (or max rounds reached).

        When the model returns a plain-text answer directly (no tool call was
        needed), yield its content straight away — no need to re-invoke.

    Phase 2 — stream tool-informed response:
        Only enters when tool_calls actually occurred. The model's final answer
        is streamed via astream() so the frontend sees token-by-token output.
    """
    llm = _get_llm()
    tools = get_tools()
    model_with_tools = llm.bind_tools(tools)

    tool_calls_occurred = False

    for _ in range(max_tool_rounds):
        try:
            response: AIMessage = await model_with_tools.ainvoke(messages)
        except Exception:
            logger.warning(
                "Tool calling not supported, falling back to plain streaming",
                exc_info=True,
            )
            async for chunk in llm.astream(messages):
                yield chunk
            return

        if not response.tool_calls:
            if tool_calls_occurred:
                # Tools were called and results fed back. The final answer
                # comes from streaming the model WITHOUT prepending its own
                # non-streaming response — otherwise it has nothing new to say.
                async for chunk in llm.astream(messages):
                    if chunk.content:
                        yield chunk.content
            else:
                # Direct answer, no tool calls needed.
                if response.content:
                    yield response.content
            return

        tool_calls_occurred = True
        messages.append(response)

        for tc in response.tool_calls:
            tool_obj = get_tool_by_name(tc["name"])
            result = await tool_obj.ainvoke(tc["args"])
            result_str = (
                json.dumps(result, ensure_ascii=False)
                if not isinstance(result, str)
                else result
            )
            messages.append(ToolMessage(content=result_str, tool_call_id=tc["id"]))

    # Max rounds exhausted — stream whatever the model produces
    async for chunk in llm.astream(messages):
        if chunk.content:
            yield chunk.content
