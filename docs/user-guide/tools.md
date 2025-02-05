# Tools Guide

Tools extend agents' capabilities by allowing them to perform specific actions.

## Built-in Tools

### WebSearchTool

Performs web searches using DuckDuckGo:

```python
from bedrock_swarm.tools.web import WebSearchTool

# Create and configure the tool
search_tool = WebSearchTool()

# Add to an agent
agent.add_tool(search_tool)
```

## Creating Custom Tools

Create custom tools by extending `BaseTool`:

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

# File operations tool example
class FileWriter(BaseTool):
    @property
    def name(self) -> str:
        return "file_writer"

    @property
    def description(self) -> str:
        return "Writes content to a file"

    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path"},
                    "content": {"type": "string", "description": "Content to write"}
                },
                "required": ["path", "content"]
            }
        }

    def _execute_impl(self, path: str, content: str) -> str:
        try:
            with open(path, "w") as f:
                f.write(content)
            return f"Successfully wrote to {path}"
        except Exception as e:
            return f"Error writing to file: {str(e)}"
```

## Tool Validation

Tools include built-in parameter validation:

```python
# Parameter type validation
def _execute_impl(self, x: int, y: float) -> str:
    # x must be int, y must be float
    return str(x + y)

# Required parameters
def get_schema(self):
    return {
        "parameters": {
            "required": ["x", "y"]  # Both parameters required
        }
    }

# Value constraints
def get_schema(self):
    return {
        "parameters": {
            "properties": {
                "count": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100
                }
            }
        }
    }
```

## Best Practices

1. **Clear Purpose**
   - Each tool should have a single, well-defined purpose
   - Use clear, descriptive names and documentation

2. **Error Handling**
   - Handle expected errors gracefully
   - Provide informative error messages
   - Return meaningful results

3. **Validation**
   - Define clear parameter schemas
   - Use appropriate type constraints
   - Validate inputs thoroughly

4. **Performance**
   - Keep tools lightweight and focused
   - Cache results when appropriate
   - Handle resources properly

5. **Testing**
   - Test with various input combinations
   - Verify error handling
   - Check edge cases
