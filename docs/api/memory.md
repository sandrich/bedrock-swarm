# Memory API Reference

## Message

```python
@dataclass
class Message:
    role: str
    content: str
    timestamp: datetime
    thread_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
```

The `Message` class represents a single message in the conversation history.

### Attributes

- `role`: The role of the message sender (`"user"`, `"assistant"`, or `"system"`)
- `content`: The actual message content
- `timestamp`: When the message was created
- `thread_id`: Optional identifier for thread-specific messages
- `metadata`: Optional dictionary of additional message data

## SimpleMemory

```python
class SimpleMemory(BaseMemory):
    def __init__(self, max_size: int = 1000) -> None:
        ...
```

The default memory implementation providing thread support and message management.

### Methods

#### add_message
```python
def add_message(self, message: Message) -> None
```
Add a message to memory. If thread's message count exceeds `max_size`, oldest messages are removed.

#### get_messages
```python
def get_messages(self, thread_id: Optional[str] = None) -> List[Message]
```
Get messages from memory, optionally filtered by thread ID.

#### get_last_message
```python
def get_last_message(self, thread_id: Optional[str] = None) -> Optional[Message]
```
Get the most recent message, optionally from a specific thread.

#### get_messages_by_type
```python
def get_messages_by_type(
    self,
    message_type: str,
    thread_id: Optional[str] = None
) -> List[Message]
```
Get messages of a specific type (e.g., "tool_result", "user_message").

#### get_tool_results
```python
def get_tool_results(
    self,
    thread_id: Optional[str] = None,
    limit: Optional[int] = None
) -> List[Message]
```
Get tool execution results, optionally limited to most recent N results.

#### get_conversation_summary
```python
def get_conversation_summary(
    self,
    thread_id: Optional[str] = None,
    limit: int = 5
) -> List[Dict[str, str]]
```
Get a summary of recent conversation exchanges.

#### clear
```python
def clear(self) -> None
```
Clear all messages and shared state.

#### clear_thread
```python
def clear_thread(self, thread_id: str) -> None
```
Clear all messages from a specific thread.

#### get_thread_ids
```python
def get_thread_ids(self) -> List[str]
```
Get list of all thread IDs in memory.

## BaseMemory

```python
class BaseMemory:
    def add_message(self, message: Message) -> None: ...
    def get_messages(self, thread_id: Optional[str] = None) -> List[Message]: ...
    def get_last_message(self, thread_id: Optional[str] = None) -> Optional[Message]: ...
    def clear(self) -> None: ...
```

Abstract base class for implementing custom memory systems.

### Required Methods

All custom memory implementations must implement these methods:

- `add_message`: Add a message to memory
- `get_messages`: Retrieve messages from memory
- `get_last_message`: Get most recent message
- `clear`: Clear all messages

## SharedState

```python
class SharedState:
    def __init__(self) -> None: ...
```

Simple key-value store for sharing state between agents.

### Methods

#### set
```python
def set(self, key: str, value: Any) -> None
```
Set a value in shared state.

#### get
```python
def get(self, key: str, default: Any = None) -> Any
```
Get a value from shared state.

#### clear
```python
def clear(self) -> None
```
Clear all shared state.

## Message Types

The memory system uses these standard message types in metadata:

- `"user_message"`: Messages from users
- `"assistant_response"`: Direct responses from assistants
- `"tool_call_intent"`: Tool execution requests
- `"tool_result"`: Results from tool executions
- `"error"`: Error messages

## Metadata Fields

Common metadata fields include:

- `"type"`: Message type identifier
- `"timestamp"`: ISO format timestamp
- `"thread_id"`: Thread identifier
- `"run_id"`: Execution run identifier
- `"tool_call_id"`: Tool execution identifier
- `"has_tool_calls"`: Boolean indicating tool usage
- `"agent"`: Name of the agent involved

## Usage Examples

### Basic Memory Usage
```python
from bedrock_swarm.memory import SimpleMemory, Message
from datetime import datetime

# Create memory system
memory = SimpleMemory(max_size=1000)

# Add a message
message = Message(
    role="user",
    content="Hello",
    timestamp=datetime.now(),
    metadata={"type": "user_message"}
)
memory.add_message(message)

# Get messages
all_messages = memory.get_messages()
thread_messages = memory.get_messages(thread_id="thread_123")
recent_message = memory.get_last_message()
```

### Thread Management
```python
# Add messages to different threads
memory.add_message(Message(
    role="user",
    content="Thread 1 message",
    timestamp=datetime.now(),
    thread_id="thread_1"
))

memory.add_message(Message(
    role="user",
    content="Thread 2 message",
    timestamp=datetime.now(),
    thread_id="thread_2"
))

# Get thread-specific messages
thread_1_msgs = memory.get_messages(thread_id="thread_1")
thread_2_msgs = memory.get_messages(thread_id="thread_2")

# Clear specific thread
memory.clear_thread("thread_1")
```

### Working with Tool Results
```python
# Get tool execution results
tool_results = memory.get_tool_results(limit=5)

# Get messages by type
tool_calls = memory.get_messages_by_type("tool_call_intent")
responses = memory.get_messages_by_type("assistant_response")
```

### Conversation Summary
```python
# Get recent conversation summary
summary = memory.get_conversation_summary(limit=3)
for exchange in summary:
    print(f"User: {exchange['user']}")
    print(f"Assistant: {exchange['assistant']}")
    print(f"Used tools: {exchange['has_tool_calls']}")
```
