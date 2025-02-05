"""Type definitions for bedrock-swarm."""

from typing import Any, Dict, Optional, TypedDict


class ToolCall(TypedDict):
    """A tool call made by an agent."""

    id: str
    type: str
    function: Dict[str, Any]


class ToolCallResult(TypedDict):
    """Result of a tool call."""

    tool_call_id: str
    output: str
    error: Optional[str]
