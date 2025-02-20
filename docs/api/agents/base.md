# Base Agent

The `BedrockAgent` class serves as the foundation for all agents in the Bedrock Swarm framework. It provides core functionality for model interaction, tool management, and memory handling.

## Class Documentation

::: bedrock_swarm.agents.base.BedrockAgent
    options:
      show_root_heading: false
      show_source: true
      heading_level: 3

## Core Features

The base agent provides:

1. **Model Integration**
   - Model initialization
   - Request formatting
   - Response processing
   - Token management

2. **Tool Management**
   - Tool registration
   - Tool validation
   - Tool execution
   - Error handling

3. **Memory System**
   - Context management
   - Message history
   - State persistence
   - Memory cleanup

## Usage Examples

```python
from bedrock_swarm.agents import BedrockAgent
from bedrock_swarm.tools import CalculatorTool

# Create agent
agent = BedrockAgent(
    name="calculator",
    model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    tools=[CalculatorTool()],
    system_prompt="You are a calculation specialist."
)

# Process message
response = agent.generate("Calculate 15 * 7")
print(response)

# Check memory
history = agent.memory.get_messages()
print(history)

# Get token usage
print(agent.last_token_count)
```

## Tool Integration

Agents can use multiple tools:

```python
from bedrock_swarm.tools import CalculatorTool, TimeTool

# Create agent with multiple tools
agent = BedrockAgent(
    name="utility_agent",
    model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    tools=[
        CalculatorTool(),
        TimeTool()
    ]
)

# Tools are available in prompts
response = agent.generate(
    "What will be 2 * 5 in 3 hours?"
)
```

## Memory Management

The agent includes memory management:

```python
# Access memory system
memory = agent.memory

# Store message
memory.add_message(
    role="user",
    content="Hello!",
    metadata={"timestamp": "2024-02-29"}
)

# Get recent messages
recent = memory.get_recent(n=5)

# Clear memory
memory.clear()
```

## Error Handling

The agent handles various errors:

1. **Model Errors**
   ```python
   try:
       response = agent.generate("Invalid request")
   except ModelInvokeError as e:
       print(f"Model error: {e}")
   ```

2. **Tool Errors**
   ```python
   try:
       response = agent.execute_tool("invalid_tool")
   except ToolError as e:
       print(f"Tool error: {e}")
   ```

3. **Memory Errors**
   ```python
   try:
       messages = agent.memory.get_messages()
   except MemoryError as e:
       print(f"Memory error: {e}")
   ```

## Implementation Details

The agent implementation includes:

1. **Request Processing**
   - Message formatting
   - Tool integration
   - Memory context
   - Response handling

2. **Tool Management**
   - Tool registration
   - Schema validation
   - Execution handling
   - Result processing

3. **Memory Integration**
   - Message storage
   - Context retrieval
   - State management
   - Cleanup handling

## Agent Configuration

Agents can be configured with:

```python
agent_config = {
    "name": "specialized_agent",
    "model_id": "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    "system_prompt": "You are a specialized agent...",
    "tools": [CalculatorTool()],
    "memory": CustomMemory(),
    "model_config": {
        "temperature": 0.7,
        "max_tokens": 1000
    }
}

agent = BedrockAgent(**agent_config)
```

## Best Practices

1. **Tool Organization**
   ```python
   # Group related tools
   math_tools = [
       CalculatorTool(),
       StatisticsTool()
   ]

   # Create specialized agent
   math_agent = BedrockAgent(
       name="math_expert",
       tools=math_tools
   )
   ```

2. **Memory Usage**
   ```python
   # Use memory for context
   agent.memory.add_context(
       key="user_preferences",
       value={"format": "metric"}
   )

   # Clear old context
   agent.memory.clear_context("old_key")
   ```

3. **Error Recovery**
   ```python
   try:
       response = agent.generate(message)
   except Exception as e:
       # Log error
       logger.error(f"Agent error: {e}")
       # Attempt recovery
       agent.reset_state()
       # Retry with fallback
       response = agent.generate_fallback(message)
   ```
