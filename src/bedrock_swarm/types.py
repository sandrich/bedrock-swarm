"""Type definitions for Bedrock Swarm."""

from typing import Any, Dict, List, Literal, Optional, TypedDict


class ToolCallFunction(TypedDict):
    """Structure of a tool call function."""

    name: str
    arguments: str  # JSON string of arguments


class ToolCall(TypedDict):
    """Structure of a tool call."""

    id: str
    type: str
    function: ToolCallFunction


class AgentResponse(TypedDict):
    """Structure of an agent's response."""

    type: str  # 'tool_call' or 'message'
    content: Optional[str]  # Present for message responses
    tool_calls: Optional[List[ToolCall]]  # Present for tool call responses


class ToolOutput(TypedDict):
    """Structure of a tool execution output."""

    tool_call_id: str
    output: str


class ToolResult(TypedDict):
    """Structure of a tool execution result."""

    success: bool
    result: str
    error: Optional[str]


# New types for event system
EventType = Literal[
    "agent_start",  # Agent begins processing
    "agent_complete",  # Agent completes processing
    "tool_start",  # Tool execution begins
    "tool_complete",  # Tool execution completes
    "message_sent",  # Message sent between agents
    "message_received",  # Message received by agent
    "error",  # Error occurred
    "run_start",  # Run begins
    "run_complete",  # Run completes
]


class Event(TypedDict):
    """Structure of a system event."""

    id: str  # Unique event ID
    type: EventType  # Type of event
    timestamp: str  # ISO format timestamp
    agent_name: str  # Name of agent involved
    run_id: str  # ID of the run this event belongs to
    thread_id: str  # ID of the thread this event belongs to
    parent_event_id: Optional[str]  # ID of parent event if any
    details: Dict[str, Any]  # Event-specific details
    metadata: Dict[str, Any]  # Additional metadata
