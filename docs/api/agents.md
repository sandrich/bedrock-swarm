# Agents API Reference

## BedrockAgent

::: bedrock_swarm.agents.base.BedrockAgent
    options:
      show_root_heading: true
      show_source: true

## Supported Models

The following AWS Bedrock models are supported:

### Anthropic Claude
- `anthropic.claude-v1`
- `anthropic.claude-v2`
- `anthropic.claude-v2:1`
- `anthropic.claude-instant-v1`

### Amazon Titan
- `amazon.titan-text-express-v1`
- `amazon.titan-text-lite-v1`

### AI21 Jurassic
- `ai21.j2-mid-v1`
- `ai21.j2-ultra-v1`

### Cohere Command
- `cohere.command-text-v14`

## Examples

### Basic Usage

```python
from bedrock_swarm import BedrockAgent
from bedrock_swarm.config import AWSConfig

# Create agent
agent = BedrockAgent(
    name="assistant",
    model_id="anthropic.claude-v2",
    aws_config=AWSConfig(region="us-west-2"),
    instructions="You are a helpful AI assistant.",
    temperature=0.7,
    max_tokens=1000
)

# Process messages
response = await agent.process_message("Hello!")
```

### With Tools

```python
# Add built-in tool
agent.add_tool("WebSearchTool")

# Add custom tool
from bedrock_swarm.tools import BaseTool

class CustomTool(BaseTool):
    name = "custom_tool"
    description = "Custom tool description"
    
    async def execute(self, **kwargs):
        return "Result"

agent.add_tool(CustomTool())
```

### With Memory

```python
from bedrock_swarm.memory import SimpleMemory

# Create agent with memory
agent = BedrockAgent(
    name="assistant",
    model_id="anthropic.claude-v2",
    aws_config=config,
    memory=SimpleMemory()
)

# Process messages
await agent.process_message("Hello!")
messages = await agent.memory.get_messages()
```

### Error Handling

```python
from bedrock_swarm.exceptions import ModelInvokeError, ToolError

try:
    response = await agent.process_message("Use the tool")
except ModelInvokeError as e:
    print(f"Model error: {e}")
except ToolError as e:
    print(f"Tool error: {e}")
``` 