# Tools API

Tools extend agents' capabilities by allowing them to perform specific actions.

## BaseTool

Abstract base class for implementing tools:

```python
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseTool(ABC):
    def __init__(self, name: str, description: str) -> None:
        self._name = name
        self._description = description
        schema = self.get_schema()
        validate_tool_schema(self.name, schema)

    @property
    @abstractmethod
    def name(self) -> str:
        """Get tool name."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Get tool description."""
        pass

    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """Get JSON schema for the tool."""
        pass

    def execute(self, **kwargs: Any) -> str:
        """Execute the tool with validation."""
        validate_tool_parameters(self.get_schema(), **kwargs)
        return self._execute_impl(**kwargs)

    @abstractmethod
    def _execute_impl(self, **kwargs: Any) -> str:
        """Implement the tool's functionality."""
        pass
```

## WebSearchTool

::: bedrock_swarm.tools.web.WebSearchTool
    options:
      show_root_heading: true
      show_source: true

## ToolFactory

::: bedrock_swarm.tools.factory.ToolFactory
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
agent.add_tool("WebSearchTool")

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

### WebSearchTool

Tool for performing web searches:

```python
from bedrock_swarm.tools.web import WebSearchTool

# Create and configure tool
search_tool = WebSearchTool()

# Execute search
result = search_tool.execute(
    query="Latest developments in AI",
    num_results=5
)
print(result)
```

#### Parameters

- `query` (str): The search query
- `num_results` (int, optional): Number of results to return (default: 5)

#### Example Response

```python
1. Latest Quantum Computing Breakthrough
   https://example.com/article1
   Description of the breakthrough...

2. Quantum Computing Research Update
   https://example.com/article2
   Recent developments in the field...
```

## Creating Custom Tools

Example of creating a custom tool:

```python
from bedrock_swarm.tools.base import BaseTool
from typing import Dict, Any

class Calculator(BaseTool):
    @property
    def name(self) -> str:
        return "calculator"

    @property
    def description(self) -> str:
        return "Performs basic arithmetic operations"

    def get_schema(self) -> Dict[str, Any]:
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

# Create and use the tool
calculator = Calculator()
result = calculator.execute(x=5, y=3, operation="multiply")
print(result)  # "5 multiply 3 = 15"
```

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
from bedrock_swarm.tools.web import WebSearchTool
from bedrock_swarm.config import AWSConfig

def main():
    # Configure AWS
    config = AWSConfig(
        region="us-west-2",
        profile="default"
    )

    # Create agent
    agent = BedrockAgent(
        name="researcher",
        model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        aws_config=config,
        instructions="You are a research assistant. Use the web search tool to find information."
    )

    # Add tools
    agent.add_tool(WebSearchTool())
    agent.add_tool(Calculator())

    # The agent will automatically use tools when needed
    response = agent.process_message(
        "What are the latest developments in AI safety? "
        "Also, what is 25 times 4?"
    )
    print(response)

if __name__ == "__main__":
    main()
```
