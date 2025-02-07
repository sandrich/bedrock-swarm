"""Base memory implementation for managing conversation history and shared state."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class Message:
    """Message class for storing conversation history."""

    role: str  # 'user', 'assistant', or 'system'
    content: str
    timestamp: datetime
    thread_id: Optional[str] = None  # To support multi-thread conversations
    metadata: Optional[Dict[str, Any]] = None


class SharedState:
    """Simple shared state between agents."""

    def __init__(self) -> None:
        """Initialize shared state."""
        self._data: Dict[str, Any] = {}

    def set(self, key: str, value: Any) -> None:
        """Set a value in shared state."""
        self._data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from shared state."""
        return self._data.get(key, default)

    def clear(self) -> None:
        """Clear all shared state."""
        self._data.clear()


class BaseMemory:
    """Base class for memory implementations."""

    def add_message(self, message: Message) -> None:
        """Add a message to memory.

        Args:
            message: Message to add
        """
        raise NotImplementedError

    def get_messages(self, thread_id: Optional[str] = None) -> List[Message]:
        """Get messages from memory.

        Args:
            thread_id: Optional thread ID to filter messages

        Returns:
            List of messages in chronological order
        """
        raise NotImplementedError

    def get_last_message(self, thread_id: Optional[str] = None) -> Optional[Message]:
        """Get the most recent message.

        Args:
            thread_id: Optional thread ID to filter messages

        Returns:
            Most recent message or None if no messages
        """
        raise NotImplementedError

    def clear(self) -> None:
        """Clear all messages from memory."""
        raise NotImplementedError


class SimpleMemory(BaseMemory):
    """Simple in-memory implementation with thread support and shared state."""

    def __init__(self, max_size: int = 1000) -> None:
        """Initialize SimpleMemory.

        Args:
            max_size: Maximum number of messages to store per thread
        """
        self._messages: Dict[str, List[Message]] = {}  # thread_id -> messages
        self._max_size = max_size
        self.shared_state = SharedState()

    def add_message(self, message: Message) -> None:
        """Add a message to memory.

        If max_size is reached, oldest messages are removed.

        Args:
            message: Message to add
        """
        thread_id = message.thread_id or "default"
        if thread_id not in self._messages:
            self._messages[thread_id] = []

        self._messages[thread_id].append(message)

        # Enforce size limit per thread
        if len(self._messages[thread_id]) > self._max_size:
            self._messages[thread_id] = self._messages[thread_id][-self._max_size :]

    def get_messages(self, thread_id: Optional[str] = None) -> List[Message]:
        """Get messages from memory.

        Args:
            thread_id: Optional thread ID to filter messages

        Returns:
            List of messages in chronological order
        """
        if thread_id:
            return self._messages.get(thread_id, []).copy()

        # If no thread_id, return all messages sorted by timestamp
        all_messages = []
        for messages in self._messages.values():
            all_messages.extend(messages)
        return sorted(all_messages, key=lambda m: m.timestamp)

    def get_last_message(self, thread_id: Optional[str] = None) -> Optional[Message]:
        """Get the most recent message.

        Args:
            thread_id: Optional thread ID to filter messages

        Returns:
            Most recent message or None if no messages
        """
        messages = self.get_messages(thread_id)
        return messages[-1] if messages else None

    def clear(self) -> None:
        """Clear all messages from memory."""
        self._messages.clear()
        self.shared_state.clear()
