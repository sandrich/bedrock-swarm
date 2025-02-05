# Core Concepts

Bedrock Swarm is built around several key concepts that work together to create powerful multi-agent systems.

## Agents

Agents are the core building blocks of the system. Each agent is powered by an AWS Bedrock model and can:

- Process messages and generate responses
- Use tools to perform actions
- Maintain conversation memory
- Follow specific instructions

```python
agent = BedrockAgent(
    name="assistant",
    model_id="anthropic.claude-v2",
    aws_config=config,
    instructions="You are a helpful AI assistant.",
    temperature=0.7,
    max_tokens=1000
)
```

### Agent Properties

- `name`: Unique identifier for the agent
- `model_id`: AWS Bedrock model to use
- `instructions`: System prompt/instructions for the agent
- `temperature`: Controls response randomness (0-1)
- `max_tokens`: Maximum response length

## Tools

Tools extend agents' capabilities by allowing them to perform specific actions:

```python
# Built-in tools
agent.add_tool("WebSearchTool")

# Custom tools
class CustomTool(BaseTool):
    @property
    def name(self) -> str:
        return "custom_tool"
    
    @property
    def description(self) -> str:
        return "Description of what the tool does"
    
    async def execute(self, **kwargs) -> str:
        # Tool implementation
        return "Result"
```

### Tool Properties

- `name`: Unique identifier for the tool
- `description`: What the tool does
- `schema`: JSON schema defining parameters
- `execute`: Implementation of the tool's functionality

## Memory

Memory systems allow agents to maintain context across conversations:

```python
class CustomMemory(BaseMemory):
    async def add_message(self, message: Message) -> None:
        # Store message
        pass
    
    async def get_messages(self) -> List[Message]:
        # Retrieve messages
        pass
    
    async def clear(self) -> None:
        # Clear memory
        pass
```

### Message Properties

- `role`: Who sent the message (human/assistant/system)
- `content`: The message content
- `timestamp`: When the message was sent
- `metadata`: Additional information

## Agency

Agencies coordinate multiple agents to solve complex tasks:

```python
agency = Agency([
    researcher,
    analyst,
    writer
])

# Sequential execution
result = await agency.execute(task)

# Parallel discussion
history = await agency.discuss(topic)
```

### Agency Features

- Task distribution
- Agent coordination
- Result aggregation
- Multi-round discussions

## Error Handling

The library provides specific exceptions for different error cases:

```python
try:
    result = await agent.process_message(message)
except ModelInvokeError:
    # Handle model API errors
except ToolError:
    # Handle tool-related errors
except ResponseParsingError:
    # Handle response parsing errors
```

### Common Exceptions

- `ModelInvokeError`: AWS Bedrock API errors
- `ToolError`: Tool-related errors
- `ToolNotFoundError`: Unknown tool requested
- `ToolExecutionError`: Tool execution failed
- `ResponseParsingError`: Invalid model response

## Best Practices

1. **Agent Design**
   - Give clear, specific instructions
   - Use appropriate temperature settings
   - Implement proper error handling

2. **Tool Implementation**
   - Make tools focused and reusable
   - Provide clear documentation
   - Handle errors gracefully

3. **Memory Management**
   - Clear memory when appropriate
   - Consider memory limitations
   - Use metadata for organization

4. **Agency Coordination**
   - Define clear agent roles
   - Break down complex tasks
   - Monitor agent interactions 