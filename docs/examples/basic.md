# Basic Usage Examples

This guide provides basic examples of using Bedrock Swarm.

## Simple Conversation

Basic interaction with an agent:

```python
from bedrock_swarm import BedrockAgent
from bedrock_swarm.config import AWSConfig

def main():
    # Configure AWS
    config = AWSConfig(
        region="us-west-2",
        profile="default"
    )

    # Create an agent
    agent = BedrockAgent(
        name="assistant",
        model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        aws_config=config
    )

    # Have a conversation
    response = agent.process_message("What is artificial intelligence?")
    print(response)

if __name__ == "__main__":
    main()
```

## Using Tools

Example of an agent using tools:

```python
from bedrock_swarm import BedrockAgent
from bedrock_swarm.tools.base import BaseTool

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
                    "x": {"type": "number", "description": "First number"},
                    "y": {"type": "number", "description": "Second number"},
                    "operation": {
                        "type": "string",
                        "description": "Operation to perform",
                        "enum": ["add", "multiply"]
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
        elif operation == "multiply":
            result = x * y
        else:
            raise ValueError(f"Unknown operation: {operation}")

        return f"{x} {operation} {y} = {result}"

def main():
    # Configure AWS
    config = AWSConfig(
        region="us-west-2",
        profile="default"
    )

    # Create agent with tool
    agent = BedrockAgent(
        name="math_assistant",
        model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        aws_config=config
    )
    agent.add_tool(Calculator())

    # Use the tool through the agent
    response = agent.process_message("What is 5 times 3?")
    print(response)

if __name__ == "__main__":
    main()
```

## Working with Memory

Example of using agent memory:

```python
from bedrock_swarm import BedrockAgent
from bedrock_swarm.memory import SimpleMemory

def main():
    # Configure AWS
    config = AWSConfig(
        region="us-west-2",
        profile="default"
    )

    # Create agent with memory
    agent = BedrockAgent(
        name="memory_assistant",
        model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        aws_config=config,
        memory=SimpleMemory()
    )

    # Have a conversation with memory
    agent.process_message("My name is Alice")
    agent.process_message("What's my name?")  # Agent remembers "Alice"

    # View memory contents
    messages = agent.memory.get_messages(limit=5)
    print(messages)

if __name__ == "__main__":
    main()
```

## Error Handling

Example of proper error handling:

```python
from bedrock_swarm import BedrockAgent
from bedrock_swarm.exceptions import ModelInvokeError, ToolError

def main():
    # Configure AWS
    config = AWSConfig(
        region="us-west-2",
        profile="default"
    )

    try:
        agent = BedrockAgent(
            name="error_handler",
            model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
            aws_config=config
        )
        response = agent.process_message("Generate a very long response")
        print(response)
    except ModelInvokeError as e:
        print(f"Model error: {e}")
    except ToolError as e:
        print(f"Tool error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
```

## Configuration

Example of configuring an agent:

```python
from bedrock_swarm import BedrockAgent

def main():
    # Configure AWS
    config = AWSConfig(
        region="us-west-2",
        profile="default"
    )

    agent = BedrockAgent(
        name="configured_assistant",
        model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        aws_config=config,
        max_tokens=2000,
        temperature=0.7,
        instructions="You are a helpful AI assistant specialized in Python programming.",
        memory=SimpleMemory(max_size=50)
    )

    response = agent.process_message("How do I write a Python decorator?")
    print(response)

if __name__ == "__main__":
    main()
```
