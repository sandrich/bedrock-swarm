# Agents API

The core agent functionality in Bedrock Swarm.

## BedrockAgent

Main agent class for interacting with AWS Bedrock models:

```python
from bedrock_swarm import BedrockAgent
from bedrock_swarm.config import AWSConfig

# Create agent
agent = BedrockAgent(
    name="assistant",
    model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    aws_config=AWSConfig(region="us-west-2"),
    instructions="You are a helpful AI assistant.",
    temperature=0.7,
    max_tokens=1000
)

# Process messages
response = agent.process_message("Hello! How can you help me?")
print(response)
```

### Configuration

Available configuration options:

```python
from bedrock_swarm import BedrockAgent
from bedrock_swarm.config import AWSConfig
from bedrock_swarm.memory import SimpleMemory

agent = BedrockAgent(
    # Required parameters
    name="assistant",
    model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    aws_config=AWSConfig(
        region="us-west-2",
        profile="default",
        endpoint_url=None  # Optional custom endpoint
    ),

    # Optional parameters
    instructions="You are a helpful AI assistant.",
    temperature=0.7,  # Controls randomness (0-1)
    max_tokens=1000,  # Maximum response length
    memory=SimpleMemory(max_size=100)  # Memory system
)
```

### Using Tools

Adding and using tools:

```python
from bedrock_swarm import BedrockAgent
from bedrock_swarm.tools.web import WebSearchTool
from bedrock_swarm.tools.base import BaseTool

# Add built-in tool
agent.add_tool(WebSearchTool())

# Create custom tool
class Calculator(BaseTool):
    @property
    def name(self) -> str:
        return "calculator"

    @property
    def description(self) -> str:
        return "Performs basic arithmetic"

    def get_schema(self):
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "x": {"type": "number"},
                    "y": {"type": "number"},
                    "operation": {
                        "type": "string",
                        "enum": ["add", "subtract", "multiply", "divide"]
                    }
                },
                "required": ["x", "y", "operation"]
            }
        }

    def _execute_impl(self, **kwargs) -> str:
        x = kwargs["x"]
        y = kwargs["y"]
        operation = kwargs["operation"]

        if operation == "add":
            result = x + y
        elif operation == "subtract":
            result = x - y
        elif operation == "multiply":
            result = x * y
        elif operation == "divide":
            if y == 0:
                return "Error: Division by zero"
            result = x / y

        return f"{x} {operation} {y} = {result}"

# Add custom tool
agent.add_tool(Calculator())

# The agent will automatically use tools when needed
response = agent.process_message("What is 5 times 3?")
print(response)
```

### Error Handling

Proper error handling:

```python
from bedrock_swarm import BedrockAgent
from bedrock_swarm.exceptions import (
    ModelInvokeError,
    ToolError,
    ResponseParsingError
)

try:
    response = agent.process_message("Your message")
    print(response)
except ModelInvokeError as e:
    print(f"Model error: {e}")
except ToolError as e:
    print(f"Tool error: {e}")
except ResponseParsingError as e:
    print(f"Response parsing error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Memory Management

Working with agent memory:

```python
from bedrock_swarm import BedrockAgent
from bedrock_swarm.memory import SimpleMemory, Message
from datetime import datetime

# Create agent with memory
agent = BedrockAgent(
    name="assistant",
    model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    aws_config=config,
    memory=SimpleMemory(max_size=100)
)

# Process messages (automatically added to memory)
agent.process_message("Remember this: The sky is blue")
agent.process_message("What did I ask you to remember?")

# Access memory directly
messages = agent.memory.get_messages(limit=5)
for msg in messages:
    print(f"{msg.role}: {msg.content}")

# Clear memory
agent.memory.clear()
```

## Supported Models

The following AWS Bedrock models are supported:

### Anthropic Claude 3.5
- `us.anthropic.claude-3-5-sonnet-20241022-v2:0`

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
    model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    aws_config=AWSConfig(region="us-west-2"),
    instructions="You are a helpful AI assistant.",
    temperature=0.7,
    max_tokens=1000
)

# Process messages
response = agent.process_message("Hello!")
```

### With Memory

```python
from bedrock_swarm.memory import SimpleMemory

# Create agent with memory
agent = BedrockAgent(
    name="assistant",
    model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    aws_config=config,
    memory=SimpleMemory()
)
```

### Error Handling

```python
from bedrock_swarm.exceptions import ModelInvokeError, ToolError

try:
    response = agent.process_message("Use the tool")
except ModelInvokeError as e:
    print(f"Model error: {e}")
except ToolError as e:
    print(f"Tool error: {e}")
```
