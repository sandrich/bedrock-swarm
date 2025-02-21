# Memory System

The Bedrock Swarm memory system provides sophisticated conversation history management and context preservation across agent interactions. This document explains how the memory system works and how to use it effectively.

## Overview

The memory system is responsible for:
- Maintaining conversation history
- Recording tool executions and their results
- Preserving context across interactions
- Managing thread-specific conversations
- Enforcing memory size limits
- Supporting metadata-rich message storage

## Core Components

### Message

Messages are the fundamental unit of memory storage. Each message includes:

```python
@dataclass
class Message:
    role: str  # 'user', 'assistant', or 'system'
    content: str
    timestamp: datetime
    thread_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
```

### Memory Types

1. **SimpleMemory**: The default implementation that provides:
   - Thread-based message organization
   - Size-limited message storage (default 1000 messages per thread)
   - Message type filtering
   - Conversation summarization
   - Tool result tracking

2. **BaseMemory**: An abstract base class for implementing custom memory systems

## Key Features

### Message Recording

The system automatically records:
- User messages with metadata
- Assistant responses with context
- Tool execution results
- Error messages
- System events

Example:
```python
# Messages are automatically recorded during interactions
response = agency.process_request("What time is it in Tokyo?")
```

### Context Management

The memory system maintains conversation context by:
- Preserving recent message history
- Including tool execution results
- Tracking conversation threads
- Managing metadata for context enrichment

Example of context usage:
```python
# The agent can reference previous interactions
User: "What is 15% of 85?"
Assistant: "15% of 85 is 12.75"

User: "Can you explain how you calculated that?"
Assistant: "I calculated this by multiplying 85 by 0.15..."
```

### Thread Management

Conversations can be organized into threads:
- Each thread maintains its own message history
- Threads can be cleared independently
- Messages can be filtered by thread ID
- Thread-specific size limits are enforced

### Metadata Support

Messages include rich metadata:
- Message type (`user_message`, `assistant_response`, `tool_result`, etc.)
- Timestamps
- Thread IDs
- Tool execution details
- Custom metadata fields

### Memory Cleanup

The system automatically manages memory usage:
- Enforces configurable size limits per thread
- Removes oldest messages when limit is reached
- Preserves most recent and relevant context
- Supports manual thread clearing

## Usage Examples

### Basic Usage
```python
from bedrock_swarm.agency import Agency
from bedrock_swarm.agents import BedrockAgent

# Create an agent with default memory system
agent = BedrockAgent(
    name="assistant",
    model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    role="Assistant"
)

# Agency automatically manages memory
agency = Agency(agents={"assistant": agent})

# Memory is handled automatically during interactions
response = agency.process_request("Hello!")
```

### Accessing Memory
```python
# Get all messages
messages = agent.memory.get_messages()

# Get messages by type
tool_results = agent.memory.get_messages_by_type("tool_result")

# Get conversation summary
summary = agent.memory.get_conversation_summary(limit=5)

# Get thread-specific messages
thread_messages = agent.memory.get_messages(thread_id="thread_123")
```

### Memory Configuration
```python
from bedrock_swarm.memory import SimpleMemory

# Create memory with custom size limit
memory = SimpleMemory(max_size=500)

# Create agent with custom memory
agent = BedrockAgent(
    name="assistant",
    model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    role="Assistant",
    memory=memory
)
```

## Best Practices

1. **Memory Size**: Configure appropriate memory size limits based on your use case
2. **Thread Management**: Use threads to organize distinct conversations
3. **Metadata Usage**: Leverage metadata for enhanced context tracking
4. **Regular Cleanup**: Clear unused threads to manage memory usage
5. **Context Windows**: Use appropriate context window sizes in prompts

## Implementation Details

The memory system is deeply integrated with:
- Thread management
- Tool execution
- Event system
- Agent responses
- Conversation context

This integration ensures:
- Automatic context preservation
- Proper message recording
- Efficient memory usage
- Thread isolation
- Metadata consistency

## Advanced Features

### Conversation Summary
Get structured summaries of recent interactions:
```python
summary = memory.get_conversation_summary(limit=5)
# Returns recent user/assistant message pairs with metadata
```

### Tool Result Tracking
Access tool execution history:
```python
tool_results = memory.get_tool_results(limit=10)
# Returns recent tool execution results
```

### Thread Management
Manage conversation threads:
```python
# Clear specific thread
memory.clear_thread("thread_123")

# Get all thread IDs
thread_ids = memory.get_thread_ids()
```

## Conclusion

The memory system is a core component that enables:
- Natural conversation flow
- Context-aware responses
- Tool execution tracking
- Efficient resource usage
- Thread isolation

By automatically managing these aspects, it allows developers to focus on building agent capabilities while ensuring proper context management and memory organization.
