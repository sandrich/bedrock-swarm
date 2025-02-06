# Tools API

Tools extend agents' capabilities by allowing them to perform specific actions.

## BaseTool

::: bedrock_swarm.tools.base.BaseTool
    handler: python
    options:
      show_root_heading: true
      show_source: true

## CurrentTimeTool

::: bedrock_swarm.tools.time.CurrentTimeTool
    handler: python
    options:
      show_root_heading: true
      show_source: true

## ToolFactory

::: bedrock_swarm.tools.factory.ToolFactory
    handler: python
    options:
      show_root_heading: true
      show_source: true

## Creating Custom Tools

To create a custom tool, inherit from `BaseTool` and implement the required methods:

```python
from bedrock_swarm.tools import BaseTool
from typing import Dict, Any

class CustomTool(BaseTool):
    @property
    def name(self) -> str:
        return "custom_tool"

    @property
    def description(self) -> str:
        return "Description of what the tool does"

    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "param1": {
                        "type": "string",
                        "description": "First parameter"
                    },
                    "param2": {
                        "type": "integer",
                        "description": "Second parameter"
                    }
                },
                "required": ["param1"]
            }
        }

    def execute(self, param1: str, param2: int = 0) -> str:
        # Implement tool functionality
        result = f"Processed {param1} with {param2}"
        return result
```

## Using Tools

### Registering Tools

```python
from bedrock_swarm.tools import ToolFactory

# Register a custom tool type
ToolFactory.register_tool_type(CustomTool)

# Create tool instance
tool = ToolFactory.create_tool("CustomTool")
```

### Adding Tools to Agents

```python
# Add by tool type name
agent.add_tool("CurrentTimeTool")

# Add tool instance
custom_tool = CustomTool()
agent.add_tool(custom_tool)
```

### Tool Management

```python
# Get tool by name
tool = agent.get_tool("custom_tool")

# Remove tool
agent.remove_tool("custom_tool")

# Clear all tools
agent.clear_tools()
```

## Built-in Tools

### CurrentTimeTool

Tool for getting the current time in different formats and timezones:

```python
from bedrock_swarm.tools.time import CurrentTimeTool

# Create and configure tool
time_tool = CurrentTimeTool()

# Get current time in ISO format
result = time_tool.execute()
print(result)  # "2024-02-06T13:48:40.722200"

# Get time in specific format and timezone
result = time_tool.execute(
    format="%Y-%m-%d %H:%M:%S",
    timezone="UTC"
)
print(result)  # "2024-02-06 13:48:40"
```

#### Parameters

- `format` (str, optional): Datetime format string (default: "iso")
- `timezone` (str, optional): Timezone name (default: "local")

## Tool Validation

Tools include built-in parameter validation:

```python
from bedrock_swarm.tools.base import BaseTool

class ValidatedTool(BaseTool):
    @property
    def name(self) -> str:
        return "validated_tool"

    @property
    def description(self) -> str:
        return "Tool with parameter validation"

    def get_schema(self):
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "count": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 10
                    },
                    "text": {
                        "type": "string",
                        "minLength": 1,
                        "maxLength": 100
                    },
                    "mode": {
                        "type": "string",
                        "enum": ["fast", "accurate"]
                    }
                },
                "required": ["count", "text"]
            }
        }

    def _execute_impl(self, **kwargs) -> str:
        # Parameters are already validated
        count = kwargs["count"]  # Will be between 1 and 10
        text = kwargs["text"]    # Will be 1-100 characters
        mode = kwargs.get("mode", "fast")  # Will be "fast" or "accurate"
        return f"Processed {text} {count} times in {mode} mode"

# Use the validated tool
tool = ValidatedTool()

# This will work
result = tool.execute(count=5, text="test", mode="fast")

# These will raise validation errors
try:
    tool.execute(count=0, text="test")  # count < minimum
except ValueError as e:
    print(e)

try:
    tool.execute(count=5, text="")  # text too short
except ValueError as e:
    print(e)

try:
    tool.execute(count=5, text="test", mode="invalid")  # invalid mode
except ValueError as e:
    print(e)
```

## Using Tools with Agents

Example of using tools with an agent:

```python
from bedrock_swarm import BedrockAgent
from bedrock_swarm.tools.time import CurrentTimeTool
from bedrock_swarm.config import AWSConfig

def main():
    # Configure AWS
    config = AWSConfig(
        region="us-west-2",
        profile="default"
    )

    # Create agent
    agent = BedrockAgent(
        name="assistant",
        model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        aws_config=config,
        instructions="You are a helpful assistant that can tell time."
    )

    # Add tools
    agent.add_tool(CurrentTimeTool())

    # The agent will automatically use tools when needed
    response = agent.process_message(
        "What time is it in UTC?"
    )
    print(response)

if __name__ == "__main__":
    main()
```
