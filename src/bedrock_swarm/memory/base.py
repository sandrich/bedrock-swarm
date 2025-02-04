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
    async def add_message(self, message: Message) -> None:
        """Add a message to memory.
        
        Args:
            message (Message): Message to add
        """
        pass
    
    @abstractmethod
    async def get_messages(
        self,
        limit: Optional[int] = None,
        before: Optional[datetime] = None,
        after: Optional[datetime] = None,
        role: Optional[str] = None
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
    async def clear(self) -> None:
        """Clear all messages from memory."""
        pass

class SimpleMemory(BaseMemory):
    """Simple in-memory implementation of BaseMemory."""
    
    def __init__(self):
        self._messages: List[Message] = []
    
    async def add_message(self, message: Message) -> None:
        self._messages.append(message)
    
    async def get_messages(
        self,
        limit: Optional[int] = None,
        before: Optional[datetime] = None,
        after: Optional[datetime] = None,
        role: Optional[str] = None
    ) -> List[Message]:
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
    
    async def clear(self) -> None:
        self._messages.clear() 