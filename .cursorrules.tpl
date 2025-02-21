# AI Assistant Instructions for Bedrock Swarm Framework

Bedrock Swarm is a framework for building multi-agent systems using Amazon Bedrock. Your role is to help users create and manage coordinated AI agent systems that can work together to solve complex tasks.

## Core Capabilities

1. **Memory and Context Management**
   - Automatic conversation history tracking
   - Thread-based memory organization
   - Tool execution result tracking
   - Context-aware responses
   - Metadata-rich message storage

2. **Agent Management**
   - Multi-agent coordination
   - Specialized agent roles
   - Tool integration
   - Event tracking
   - Thread management

3. **Tool System**
   - Built-in utility tools
   - Custom tool creation
   - Tool result tracking
   - Error handling
   - Thread-aware execution

## Memory System Usage

### 1. Basic Memory Operations

```python
from bedrock_swarm.agency import Agency
from bedrock_swarm.agents import BedrockAgent
from bedrock_swarm.memory import SimpleMemory

# Create agent with memory
agent = BedrockAgent(
    name="assistant",
    model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    role="Assistant",
    memory=SimpleMemory(max_size=1000)
)

# Agency automatically handles memory
agency = Agency(agents={"assistant": agent})

# Memory is recorded automatically
response = agency.process_request("What's the weather?")

# Access conversation history
messages = agent.memory.get_messages()
last_message = agent.memory.get_last_message()
tool_results = agent.memory.get_tool_results()
```

### 2. Thread Management

```python
# Messages are automatically organized by thread
response1 = agency.process_request(
    "Question about math",
    agent_name="assistant",
    thread_id="math_thread"
)

response2 = agency.process_request(
    "Question about weather",
    agent_name="assistant",
    thread_id="weather_thread"
)

# Access thread-specific messages
math_messages = agent.memory.get_messages(thread_id="math_thread")
weather_messages = agent.memory.get_messages(thread_id="weather_thread")

# Clear specific thread
agent.memory.clear_thread("math_thread")
```

### 3. Context and History

```python
# The system maintains context automatically
responses = [
    agency.process_request("What is 15% of 85?"),
    agency.process_request("Can you explain that calculation?"),
    agency.process_request("And what if we doubled that?")
]

# Get conversation summary
summary = agent.memory.get_conversation_summary(limit=3)
```

## Agent System Usage

### 1. Creating Specialized Agents

```python
from bedrock_swarm.tools import CalculatorTool, CurrentTimeTool

# Math specialist
math_agent = BedrockAgent(
    name="math_expert",
    model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    role="Mathematics specialist",
    tools=[CalculatorTool()],
    system_prompt="You are a mathematics expert."
)

# Time specialist
time_agent = BedrockAgent(
    name="time_expert",
    model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    role="Time zone specialist",
    tools=[CurrentTimeTool()],
    system_prompt="You are a time zone expert."
)

# Create agency with specialists
agency = Agency(agents={
    "math": math_agent,
    "time": time_agent
})
```

### 2. Tool Integration

```python
from bedrock_swarm.tools import BaseTool
from pydantic import Field

# Custom tool example
class TemperatureTool(BaseTool):
    """Tool for temperature conversions."""

    celsius: float = Field(..., description="Temperature in Celsius")

    def _execute_impl(self, **kwargs) -> str:
        c = kwargs["celsius"]
        f = (c * 9/5) + 32
        return f"{c}°C is equal to {f}°F"

# Create agent with custom tool
temp_agent = BedrockAgent(
    name="temp_converter",
    model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    role="Temperature conversion specialist",
    tools=[TemperatureTool()]
)
```

### 3. Event Handling

```python
# Events are automatically tracked
response = agency.process_request("Convert 25°C to Fahrenheit")

# Events include:
# - agent_start: When agent begins processing
# - tool_start: When tool execution begins
# - tool_complete: When tool execution finishes
# - agent_complete: When agent completes response
# - error: When errors occur
```

## Best Practices

1. **Memory Management**
   - Use thread IDs to organize conversations
   - Configure appropriate memory size limits
   - Clear unused threads regularly
   - Leverage metadata for context tracking

2. **Agent Design**
   - Create focused, specialized agents
   - Provide clear system prompts
   - Include only relevant tools
   - Use descriptive agent names and roles

3. **Tool Development**
   - Write clear tool descriptions
   - Include comprehensive parameter validation
   - Handle errors gracefully
   - Return informative results

4. **Context Handling**
   - Let the system manage context automatically
   - Use appropriate context window sizes
   - Leverage conversation summaries
   - Track tool results for context

## Common Patterns

### 1. Multi-Step Conversations

```python
# The system maintains context across multiple interactions
responses = []
thread_id = "math_session"

responses.append(agency.process_request(
    "What is 15% of 85?",
    agent_name="math",
    thread_id=thread_id
))

responses.append(agency.process_request(
    "Can you explain that calculation?",
    agent_name="math",
    thread_id=thread_id
))

responses.append(agency.process_request(
    "Now calculate 25% of that result",
    agent_name="math",
    thread_id=thread_id
))
```

### 2. Tool Result Usage

```python
# Tools record their results in memory
response = agency.process_request(
    "What time is it in Tokyo?",
    agent_name="time"
)

# Access tool results
tool_results = agent.memory.get_tool_results()
time_results = agent.memory.get_messages_by_type("tool_result")
```

### 3. Error Handling

```python
try:
    response = agency.process_request("Invalid request")
except Exception as e:
    # Errors are recorded in memory
    error_messages = agent.memory.get_messages_by_type("error")
```

## Implementation Guidelines

1. **Memory Integration**
   - Memory is handled automatically
   - No manual message recording needed
   - Context is preserved automatically
   - Tool results are tracked automatically

2. **Thread Management**
   - Use meaningful thread IDs
   - One thread per conversation topic
   - Clear threads when done
   - Monitor thread sizes

3. **Tool Usage**
   - Tools are called automatically
   - Results are recorded in memory
   - Context includes tool results
   - Errors are handled gracefully

4. **Context Awareness**
   - System maintains conversation flow
   - Previous messages are accessible
   - Tool results provide context
   - Metadata enriches context

Remember:
- Let the system handle memory management
- Use thread IDs for organization
- Leverage built-in context management
- Monitor memory usage
- Clear unused threads
- Track tool results
- Handle errors appropriately
