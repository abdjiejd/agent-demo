"""Tool registry and execution for agent function calling."""

from __future__ import annotations

from typing import Any

from langchain_core.tools import BaseTool, tool


@tool
async def get_weather(city: str) -> dict[str, Any]:
    """查询指定城市的当前天气信息"""
    return {
        "city": city,
        "temperature": "25",
        "unit": "摄氏度",
        "condition": "晴天",
        "humidity": "40%",
        "wind": "3级",
    }


# All available tools
_TOOLS = [get_weather]
_TOOL_REGISTRY: dict[str, BaseTool] = {t.name: t for t in _TOOLS}


def get_tools() -> list[BaseTool]:
    """Return LangChain tool objects for binding to a model."""
    return _TOOLS


def get_tool_by_name(name: str) -> BaseTool:
    """Look up a LangChain tool by name."""
    tool_obj = _TOOL_REGISTRY.get(name)
    if tool_obj is None:
        raise ValueError(f"Unknown tool: {name}")
    return tool_obj
