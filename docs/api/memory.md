# Memory API

The memory system in Bedrock Swarm allows agents to maintain conversation history and context.

## BaseMemory

Abstract base class for memory implementations:

```python
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from bedrock_swarm.memory import Message

class BaseMemory(ABC):
    @abstractmethod
    def add_message(self, message: Message) -> None:
        """Add a message to memory."""
        pass

    @abstractmethod
    def get_messages(
        self,
        limit: Optional[int] = None,
        before: Optional[datetime] = None,
        after: Optional[datetime] = None,
        role: Optional[str] = None,
    ) -> List[Message]:
        """Get messages from memory."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear all messages from memory."""
        pass
```

## SimpleMemory

Basic in-memory implementation:

```python
from bedrock_swarm.memory import SimpleMemory, Message

# Create memory system
memory = SimpleMemory(max_size=1000)

# Add messages
memory.add_message(Message(
    role="human",
    content="Hello!",
    timestamp=datetime.now()
))

# Get messages
messages = memory.get_messages(limit=10)

# Clear memory
memory.clear()
```

## Message

Data class for messages:

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any

@dataclass
class Message:
    role: str
    content: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None
```

## Usage Example

Example of using memory in an agent:

```python
from bedrock_swarm import BedrockAgent
from bedrock_swarm.memory import SimpleMemory
from bedrock_swarm.config import AWSConfig

def main():
    # Configure AWS
    config = AWSConfig(
        region="us-west-2",
        profile="default"
    )

    # Create agent with memory
    agent = BedrockAgent(
        name="assistant",
        model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        aws_config=config,
        memory=SimpleMemory(max_size=100)
    )

    # Have a conversation
    agent.process_message("My name is Alice")
    agent.process_message("What's my name?")  # Agent remembers "Alice"

    # View memory contents
    messages = agent.memory.get_messages(limit=5)
    for msg in messages:
        print(f"{msg.role}: {msg.content}")

if __name__ == "__main__":
    main()
```

## Creating Custom Memory Systems

To create a custom memory system, inherit from `BaseMemory`:

```python
from bedrock_swarm.memory import BaseMemory, Message
from typing import List, Optional
from datetime import datetime

class CustomMemory(BaseMemory):
    def __init__(self):
        self._messages = []

    def add_message(self, message: Message) -> None:
        # Add custom processing here
        self._messages.append(message)

    def get_messages(
        self,
        limit: Optional[int] = None,
        before: Optional[datetime] = None,
        after: Optional[datetime] = None,
        role: Optional[str] = None
    ) -> List[Message]:
        messages = self._messages

        # Apply filters
        if before:
            messages = [m for m in messages if m.timestamp < before]
        if after:
            messages = [m for m in messages if m.timestamp > after]
        if role:
            messages = [m for m in messages if m.role == role]
        if limit:
            messages = messages[-limit:]

        return messages

    def clear(self) -> None:
        self._messages.clear()
```

## Best Practices

1. **Memory Management**
   - Clear memory periodically to prevent excessive memory usage
   - Use appropriate filters when retrieving messages
   - Include relevant metadata for better organization

2. **Message Structure**
   - Use appropriate roles (human/assistant/system)
   - Include accurate timestamps
   - Add helpful metadata when needed

3. **Custom Implementations**
   - Consider persistence requirements
   - Implement efficient filtering
   - Handle concurrent access if needed
