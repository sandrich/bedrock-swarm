# Send Message Tool

The `SendMessageTool` facilitates communication between agents in the Bedrock Swarm framework. It provides a standardized way to send and receive messages between agents, with support for different message types and delivery options.

## Class Documentation

::: bedrock_swarm.tools.send_message.SendMessageTool
    options:
      show_root_heading: false
      show_source: true
      heading_level: 3

## Features

The send message tool supports:

1. Message Types:
   - Text messages
   - Structured data
   - Binary content
   - Event notifications

2. Delivery Options:
   - Synchronous sending
   - Asynchronous delivery
   - Broadcast messages
   - Direct messages

3. Message Properties:
   - Priority levels
   - Delivery status
   - Message metadata
   - Timestamps

## Usage Examples

```python
from bedrock_swarm.tools import SendMessageTool

message_tool = SendMessageTool()

# Send a simple message
await message_tool.send(
    recipient="agent_id",
    content="Hello, how are you?",
    priority="normal"
)

# Send structured data
data = {
    "type": "task_update",
    "status": "completed",
    "timestamp": "2024-02-29T15:30:45Z"
}
await message_tool.send(
    recipient="agent_id",
    content=data,
    priority="high"
)

# Broadcast message
await message_tool.broadcast(
    content="System maintenance in 5 minutes",
    priority="high"
)
```

## Error Handling

The send message tool handles:

1. Invalid recipients
2. Message delivery failures
3. Network errors
4. Invalid message formats
5. Timeout conditions

## Implementation Details

The tool implementation includes:

1. Message queuing system
2. Delivery confirmation
3. Retry mechanisms
4. Priority handling
5. Error recovery

## Message Format

Messages follow this structure:

```python
{
    "id": "msg_123",
    "sender": "agent_a",
    "recipient": "agent_b",
    "content": "Message content",
    "priority": "normal",
    "timestamp": "2024-02-29T15:30:45Z",
    "metadata": {
        "type": "text",
        "version": "1.0"
    }
}
```
