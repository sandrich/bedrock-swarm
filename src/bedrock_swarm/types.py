"""Type definitions for Bedrock Swarm."""

from typing import Any, Dict, List, Literal, Optional, TypedDict, Union


class ToolCallFunction(TypedDict):
    """Structure of a tool call function."""

    name: str
    arguments: Dict[str, Any]  # Now supports direct dict arguments


class ToolCall(TypedDict):
    """Structure of a tool call."""

    id: str
    type: Literal["function"]
    function: ToolCallFunction


class ToolOutput(TypedDict):
    """Structure of a tool execution output."""

    tool_call_id: str
    output: str


class MessageResponse(TypedDict):
    """Structure of a message response."""

    type: Literal["message"]
    content: str


class ToolCallResponse(TypedDict):
    """Structure of a tool call response."""

    type: Literal["tool_call"]
    tool_calls: List[ToolCall]


AgentResponse = Union[MessageResponse, ToolCallResponse]


class EventData(TypedDict):
    """Structure of an event."""

    id: str
    type: str
    timestamp: str
    agent_name: str
    run_id: str
    thread_id: str
    details: Dict[str, Any]
    parent_id: Optional[str]


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
