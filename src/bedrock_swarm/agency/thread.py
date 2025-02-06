"""Thread implementation for agent conversations."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from ..agents.base import BedrockAgent
from ..tools.base import BaseTool
from ..types import ToolCallResult


@dataclass
class ThreadMessage:
    """A message in a thread."""

    content: str
    role: str
    timestamp: datetime = field(default_factory=datetime.now)
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_results: Optional[List[ToolCallResult]] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary format."""
        result: Dict[str, Any] = {
            "content": self.content,
            "role": self.role,
            "timestamp": self.timestamp.isoformat(),
        }
        if self.tool_calls:
            result["tool_calls"] = self.tool_calls
        if self.tool_call_results:
            result["tool_call_results"] = [
                {
                    "tool_call_id": r["tool_call_id"],
                    "output": r["output"],
                    "error": r["error"],
                }
                for r in self.tool_call_results
            ]
        if self.metadata:
            result["metadata"] = self.metadata
        return result


class Thread:
    """A thread of conversation with an agent."""

    def __init__(self, agent: Optional[BedrockAgent] = None) -> None:
        """Initialize a thread.

        Args:
            agent: Optional agent to use for this thread
        """
        self.thread_id = str(uuid4())
        self.agent = agent
        self.history: List[ThreadMessage] = []
        self.active_tools: Dict[str, BaseTool] = {}

    def execute(
        self, message: str, tool_results: Optional[List[ToolCallResult]] = None
    ) -> ThreadMessage:
        """Execute a message in the thread.

        Args:
            message: Message to execute
            tool_results: Optional results from previous tool calls

        Returns:
            Response message from the agent

        Raises:
            ValueError: If thread has no agent
        """
        if not self.agent:
            raise ValueError("Thread has no agent assigned")

        # Add human message to history
        human_message = ThreadMessage(
            content=message,
            role="human",
            tool_call_results=tool_results,
        )
        self.history.append(human_message)

        # Process message with agent
        response = self.agent.process_message(message, None)

        # Add assistant response to history
        assistant_message = ThreadMessage(
            content=response,
            role="assistant",
        )
        self.history.append(assistant_message)

        return assistant_message

    def get_history(self, limit: Optional[int] = None) -> List[ThreadMessage]:
        """Get thread history.

        Args:
            limit: Optional limit on number of messages to return

        Returns:
            List of messages in the thread
        """
        if limit:
            return self.history[-limit:]
        return self.history

    def get_formatted_history(
        self, limit: Optional[int] = None, include_tools: bool = True
    ) -> List[Dict[str, Any]]:
        """Get formatted thread history.

        Args:
            limit: Optional limit on number of messages to return
            include_tools: Whether to include tool calls and results

        Returns:
            List of formatted messages
        """
        messages = self.get_history(limit)
        formatted = []
        for msg in messages:
            formatted_msg = msg.to_dict()
            if not include_tools:
                formatted_msg.pop("tool_calls", None)
                formatted_msg.pop("tool_call_results", None)
            formatted.append(formatted_msg)
        return formatted

    def clear_history(self) -> None:
        """Clear thread history."""
        self.history.clear()
