from collections.abc import AsyncIterator

from openai import AsyncOpenAI

from app.config import settings

_client: AsyncOpenAI | None = None

SYSTEM_PROMPT = "你是一个有用的AI助手，请用中文回答用户的问题。"


def _get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(
            api_key=settings.ARK_API_KEY,
            base_url=settings.ARK_BASE_URL,
        )
    return _client


async def stream_chat(messages: list[dict]) -> AsyncIterator[str]:
    client = _get_client()
    stream = await client.chat.completions.create(
        model=settings.ARK_MODEL,
        messages=messages,
        stream=True,
    )
    async for chunk in stream:
        delta = chunk.choices[0].delta if chunk.choices else None
        if delta and delta.content:
            yield delta.content
