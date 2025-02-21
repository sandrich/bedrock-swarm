# Type System

The Bedrock Swarm type system provides strict typing for all major components using Python's type hints and TypedDict classes.

## Tool Types

### ToolCallFunction
Structure for tool function calls:
```python
class ToolCallFunction(TypedDict):
    name: str  # Name of the tool to call
    arguments: Dict[str, Any]  # Arguments for the tool
```

### ToolCall
Complete tool call structure:
```python
class ToolCall(TypedDict):
    id: str  # Unique identifier
    type: Literal["function"]  # Always "function"
    function: ToolCallFunction  # Tool function details
```

### ToolOutput
Tool execution result:
```python
class ToolOutput(TypedDict):
    tool_call_id: str  # ID of the original tool call
    output: str  # Tool execution output
```

### ToolResult
Detailed tool execution result:
```python
class ToolResult(TypedDict):
    success: bool  # Whether the tool executed successfully
    result: str  # Tool output if successful
    error: Optional[str]  # Error message if failed
```

## Message Types

### MessageResponse
Direct message response:
```python
class MessageResponse(TypedDict):
    type: Literal["message"]  # Indicates direct message
    content: str  # Message content
```

### ToolCallResponse
Response indicating tool usage:
```python
class ToolCallResponse(TypedDict):
    type: Literal["tool_call"]  # Indicates tool call
    tool_calls: List[ToolCall]  # List of tools to call
```

### AgentResponse
Union type for all possible agent responses:
```python
AgentResponse = Union[MessageResponse, ToolCallResponse]
```

## Event Types

### EventType
Literal type for all possible event types:
```python
EventType = Literal[
    "agent_start",      # Agent begins processing
    "agent_complete",   # Agent completes processing
    "tool_start",      # Tool execution begins
    "tool_complete",    # Tool execution completes
    "message_sent",     # Message sent between agents
    "message_received", # Message received by agent
    "error",           # Error occurred
    "run_start",       # Run begins
    "run_complete",    # Run completes
]
```

### Event
Complete event structure:
```python
class Event(TypedDict):
    id: str  # Unique event ID
    type: EventType  # Type of event
    timestamp: str  # ISO format timestamp
    agent_name: str  # Name of agent involved
    run_id: str  # ID of the run
    thread_id: str  # ID of the thread
    parent_event_id: Optional[str]  # ID of parent event
    details: Dict[str, Any]  # Event-specific details
    metadata: Dict[str, Any]  # Additional metadata
```

## Usage Examples

### Tool Call Flow
```python
# Create a tool call
tool_call: ToolCall = {
    "id": "call_123",
    "type": "function",
    "function": {
        "name": "calculator",
        "arguments": {"x": 5, "y": 3}
    }
}

# Tool output
output: ToolOutput = {
    "tool_call_id": "call_123",
    "output": "8"
}

# Tool result
result: ToolResult = {
    "success": True,
    "result": "8",
    "error": None
}
```

### Agent Response Flow
```python
# Direct message
message: MessageResponse = {
    "type": "message",
    "content": "The result is 8"
}

# Tool call response
tool_response: ToolCallResponse = {
    "type": "tool_call",
    "tool_calls": [tool_call]  # From previous example
}
```

### Event Flow
```python
# Create an event
event: Event = {
    "id": "evt_123",
    "type": "tool_start",
    "timestamp": "2024-02-21T14:30:00Z",
    "agent_name": "calculator",
    "run_id": "run_456",
    "thread_id": "thread_789",
    "parent_event_id": None,
    "details": {"tool_name": "calculator"},
    "metadata": {"duration_ms": 150}
}
```

## Type Safety

The type system ensures:
1. Correct structure of all data objects
2. Proper event type usage
3. Complete tool call information
4. Consistent message formats
5. Proper event chaining

## Best Practices

1. **Use Type Hints**:
   ```python
   def process_tool_call(call: ToolCall) -> ToolResult:
       # Function implementation
       pass
   ```

2. **Handle All Response Types**:
   ```python
   def handle_response(response: AgentResponse) -> str:
       if response["type"] == "message":
           return response["content"]
       else:  # tool_call
           return process_tool_calls(response["tool_calls"])
   ```

3. **Event Chain Tracking**:
   ```python
   def create_child_event(
       parent: Event,
       type: EventType,
       details: Dict[str, Any]
   ) -> Event:
       return {
           "id": generate_id(),
           "type": type,
           "parent_event_id": parent["id"],
           # ... other fields
       }
   ```
