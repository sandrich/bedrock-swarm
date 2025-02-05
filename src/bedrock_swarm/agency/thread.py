"""Thread implementation for managing agent conversations."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from ..agents.base import BedrockAgent
from ..types import ToolCallResult


@dataclass
class ThreadMessage:
    """A message in a thread."""

    role: str
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    tool_call_results: List[ToolCallResult] = field(default_factory=list)


class Thread:
    """A thread represents a conversation between a user and an agent."""

    def __init__(self, agent: Optional[BedrockAgent] = None) -> None:
        """Initialize a new thread with a unique ID.

        Args:
            agent (Optional[BedrockAgent]): The agent to use for this thread
        """
        self.thread_id: str = str(uuid4())
        self.history: List[ThreadMessage] = []
        self.active_tools: Dict[str, Dict[str, Any]] = {}
        self.agent = agent

    def clear_history(self) -> None:
        """Clear the thread history."""
        self.history = []
        self.active_tools = {}

    def get_history(self, limit: Optional[int] = None) -> List[ThreadMessage]:
        """Get the thread history.

        Args:
            limit (Optional[int]): Maximum number of messages to return

        Returns:
            List[ThreadMessage]: List of messages in the thread
        """
        if limit is not None:
            return self.history[-limit:]
        return self.history

    def execute(
        self,
        message: str,
        tool_results: Optional[List[ToolCallResult]] = None,
    ) -> ThreadMessage:
        """Execute a message in the thread.

        Args:
            message (str): The message to execute
            tool_results (Optional[List[ToolCallResult]]): Results from previous tool calls

        Returns:
            ThreadMessage: The response message

        Raises:
            ValueError: If no agent is assigned to this thread
        """
        if not self.agent:
            raise ValueError("No agent assigned to this thread")

        # Add message to history
        msg = ThreadMessage(role="human", content=message)
        if tool_results:
            msg.tool_call_results = tool_results
        self.history.append(msg)

        # Process message
        response = self.agent.process_message(message, tool_results)

        # Add response to history
        response_msg = ThreadMessage(role="assistant", content=response)
        self.history.append(response_msg)

        return response_msg

    def get_formatted_history(
        self, limit: Optional[int] = None, include_tools: bool = True
    ) -> List[Dict[str, Any]]:
        """Get the conversation history in a formatted dictionary format.

        Args:
            limit (Optional[int]): Maximum number of messages to return
            include_tools (bool): Whether to include tool calls and results

        Returns:
            List[Dict[str, Any]]: List of formatted messages
        """
        history = self.get_history(limit)
        formatted = []

        for msg in history:
            formatted_msg = {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat(),
            }

            if include_tools:
                if msg.tool_calls:
                    formatted_msg["tool_calls"] = msg.tool_calls
                if msg.tool_call_results:
                    if isinstance(msg.tool_call_results, list):
                        formatted_msg["tool_call_results"] = [
                            result if isinstance(result, dict) else result.dict()
                            for result in msg.tool_call_results
                        ]
                    else:
                        formatted_msg["tool_call_results"] = msg.tool_call_results

            formatted.append(formatted_msg)

        return formatted
