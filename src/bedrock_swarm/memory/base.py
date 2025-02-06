"""Module for managing agent memory and conversation history."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class Message:
    """A message in the conversation history.

    Attributes:
        role (str): Role of the sender (e.g., "human", "assistant", "system")
        content (str): Message content
        timestamp (datetime): When the message was sent
        metadata (Optional[Dict[str, Any]]): Additional message metadata
    """

    role: str
    content: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None


class BaseMemory(ABC):
    """Base class for memory systems.

    Memory systems are responsible for storing and retrieving conversation history
    and other relevant information for agents.
    """

    @abstractmethod
    def add_message(self, message: Message) -> None:
        """Add a message to memory.

        Args:
            message (Message): Message to add
        """
        pass

    @abstractmethod
    def get_messages(
        self,
        limit: Optional[int] = None,
        before: Optional[datetime] = None,
        after: Optional[datetime] = None,
        role: Optional[str] = None,
    ) -> List[Message]:
        """Get messages from memory.

        Args:
            limit (Optional[int]): Maximum number of messages to return
            before (Optional[datetime]): Get messages before this time
            after (Optional[datetime]): Get messages after this time
            role (Optional[str]): Filter by sender role

        Returns:
            List[Message]: List of messages matching criteria
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear all messages from memory."""
        pass


class SimpleMemory(BaseMemory):
    """Simple in-memory implementation of BaseMemory."""

    def __init__(self, max_size: int = 1000) -> None:
        """Initialize the memory system.

        Args:
            max_size (int): Maximum number of messages to store
        """
        self._messages: List[Message] = []
        self._max_size = max_size

    def add_message(self, message: Message) -> None:
        """Add a message to memory.

        Args:
            message (Message): Message to add
        """
        self._messages.append(message)
        # Remove oldest messages if we exceed max size
        if len(self._messages) > self._max_size:
            self._messages = self._messages[-self._max_size :]

    def get_messages(
        self,
        limit: Optional[int] = None,
        before: Optional[datetime] = None,
        after: Optional[datetime] = None,
        role: Optional[str] = None,
    ) -> List[Message]:
        """Get messages from memory.

        Args:
            limit (Optional[int]): Maximum number of messages to return
            before (Optional[datetime]): Get messages before this time
            after (Optional[datetime]): Get messages after this time
            role (Optional[str]): Filter by sender role

        Returns:
            List[Message]: List of messages matching criteria
        """
        messages = self._messages

        if before:
            messages = [m for m in messages if m.timestamp < before]

        if after:
            messages = [m for m in messages if m.timestamp > after]

        if role:
            messages = [m for m in messages if m.role == role]

        if limit:
            messages = messages[-limit:]

        return messages

    def get_last_message(self) -> Optional[Message]:
        """Get the most recent message.

        Returns:
            Optional[Message]: The most recent message, or None if no messages exist
        """
        messages = self.get_messages(limit=1)
        return messages[0] if messages else None

    def get_messages_by_role(self, role: str) -> List[Message]:
        """Get all messages with a specific role.

        Args:
            role (str): Role to filter by (e.g., "human", "assistant", "system")

        Returns:
            List[Message]: List of messages with the specified role
        """
        return self.get_messages(role=role)

    def clear(self) -> None:
        """Clear all messages from memory."""
        self._messages.clear()
