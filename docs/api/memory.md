# Memory API Reference

## BaseMemory

::: bedrock_swarm.memory.base.BaseMemory
    options:
      show_root_heading: true
      show_source: true

## SimpleMemory

::: bedrock_swarm.memory.base.SimpleMemory
    options:
      show_root_heading: true
      show_source: true

## Message

::: bedrock_swarm.memory.base.Message
    options:
      show_root_heading: true
      show_source: true

## Using Memory

### Basic Usage

```python
from bedrock_swarm.memory import SimpleMemory, Message
from datetime import datetime

# Create memory system
memory = SimpleMemory()

# Add messages
await memory.add_message(Message(
    role="human",
    content="Hello!",
    timestamp=datetime.now()
))

await memory.add_message(Message(
    role="assistant",
    content="Hi there!",
    timestamp=datetime.now()
))

# Retrieve messages
messages = await memory.get_messages()
for msg in messages:
    print(f"{msg.role}: {msg.content}")
```

### Filtering Messages

```python
from datetime import datetime, timedelta

# Get recent messages
now = datetime.now()
recent = await memory.get_messages(
    after=now - timedelta(minutes=5)
)

# Get messages by role
human_msgs = await memory.get_messages(role="human")

# Get limited number of messages
last_3 = await memory.get_messages(limit=3)
```

### With Metadata

```python
# Add message with metadata
await memory.add_message(Message(
    role="system",
    content="Configuration updated",
    timestamp=datetime.now(),
    metadata={
        "config_type": "model",
        "changes": ["temperature", "max_tokens"]
    }
))

# Filter by examining metadata
messages = await memory.get_messages()
config_msgs = [
    msg for msg in messages
    if msg.metadata and msg.metadata.get("config_type") == "model"
]
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
    
    async def add_message(self, message: Message) -> None:
        # Add custom processing here
        self._messages.append(message)
    
    async def get_messages(
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
    
    async def clear(self) -> None:
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