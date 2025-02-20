# Tool Development Guide

This guide explains how to develop new tools for the Bedrock Swarm framework.

## Tool Architecture

Tools in Bedrock Swarm follow a consistent architecture:

1. **Base Class**: All tools inherit from `BaseTool`
2. **Interface**: Tools implement standard methods
3. **Configuration**: Tools use consistent configuration
4. **Documentation**: Tools include comprehensive docs

## Creating a New Tool

### 1. Tool Structure

Create a new file in `bedrock_swarm/tools/`:

```python
from bedrock_swarm.tools.base import BaseTool

class CustomTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="custom_tool",
            description="Description of your tool"
        )

    async def invoke(self, **kwargs):
        # Tool implementation
        pass

    def validate_input(self, **kwargs):
        # Input validation
        pass
```

### 2. Required Methods

Implement these required methods:

1. `__init__`: Tool initialization
2. `invoke`: Main tool functionality
3. `validate_input`: Input validation

### 3. Optional Methods

Consider implementing:

1. `cleanup`: Resource cleanup
2. `setup`: Initial setup
3. `get_status`: Tool status

## Best Practices

### 1. Input Validation

Always validate inputs:

```python
def validate_input(self, **kwargs):
    if "required_param" not in kwargs:
        raise ValueError("Missing required parameter")
    if not isinstance(kwargs["required_param"], str):
        raise TypeError("Parameter must be string")
```

### 2. Error Handling

Implement comprehensive error handling:

```python
async def invoke(self, **kwargs):
    try:
        # Tool logic
        result = await self._process_request(kwargs)
        return result
    except ConnectionError:
        raise ToolError("Connection failed")
    except ValueError as e:
        raise ToolError(f"Invalid input: {e}")
```

### 3. Documentation

Include detailed documentation:

```python
class CustomTool(BaseTool):
    """Custom tool for specific functionality.

    This tool provides [description of functionality].

    Args:
        param1 (str): Description of param1
        param2 (int): Description of param2

    Returns:
        dict: Description of return value

    Raises:
        ToolError: When [error condition]
        ValueError: When [error condition]
    """
```

## Testing Tools

### 1. Test Structure

Create tests in `tests/tools/`:

```python
import pytest
from bedrock_swarm.tools import CustomTool

def test_custom_tool_initialization():
    tool = CustomTool()
    assert tool.name == "custom_tool"

@pytest.mark.asyncio
async def test_custom_tool_invoke():
    tool = CustomTool()
    result = await tool.invoke(param="value")
    assert result == expected_value
```

### 2. Test Coverage

Test these aspects:

1. Initialization
2. Input validation
3. Normal operation
4. Error conditions
5. Edge cases

## Tool Registration

Register your tool in `bedrock_swarm/tools/__init__.py`:

```python
from .custom_tool import CustomTool

__all__ = [
    "CustomTool",
    # Other tools...
]
```

## Example Tool

Complete example of a custom tool:

```python
from typing import Any, Dict
from bedrock_swarm.tools.base import BaseTool
from bedrock_swarm.exceptions import ToolError

class ExampleTool(BaseTool):
    """Example tool implementation.

    This tool demonstrates the standard structure
    and best practices for tool development.
    """

    def __init__(self):
        super().__init__(
            name="example_tool",
            description="An example tool implementation"
        )
        self._initialized = False

    async def setup(self):
        """Initialize tool resources."""
        self._initialized = True

    def validate_input(self, **kwargs):
        """Validate tool inputs."""
        required = ["input_text"]
        for param in required:
            if param not in kwargs:
                raise ValueError(f"Missing {param}")

    async def invoke(self, **kwargs) -> Dict[str, Any]:
        """Execute the tool functionality.

        Args:
            input_text (str): Text to process
            optional_param (int, optional): Optional parameter

        Returns:
            dict: Processing results

        Raises:
            ToolError: On processing failure
        """
        try:
            self.validate_input(**kwargs)
            result = await self._process(kwargs["input_text"])
            return {"status": "success", "result": result}
        except Exception as e:
            raise ToolError(f"Tool execution failed: {e}")

    async def cleanup(self):
        """Clean up tool resources."""
        self._initialized = False
```
