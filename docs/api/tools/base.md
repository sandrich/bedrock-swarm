# Base Tool

The `BaseTool` class serves as the foundation for all tool implementations in the Bedrock Swarm framework. It defines the core interface and shared functionality that all tools must implement.

## Class Documentation

::: bedrock_swarm.tools.base.BaseTool
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3

## Usage Example

```python
from bedrock_swarm.tools.base import BaseTool

class CustomTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="custom_tool",
            description="A custom tool implementation"
        )

    def _execute_impl(self, **kwargs):
        # Custom implementation
        pass
```

## Core Features

The base tool provides:

1. **Name and Description**: Tool identification
2. **Input Validation**: Common validation methods
3. **Error Handling**: Standardized error handling
4. **Documentation**: Built-in documentation support
5. **Type Safety**: TypeScript interface definitions

## Common Methods

All tool implementations inherit these methods:

- `invoke`: Abstract method for tool execution
- `validate_input`: Input validation method
- `get_description`: Returns tool description
- `get_name`: Returns tool name

## Error Handling

The base tool includes error handling for:

1. Invalid inputs
2. Missing parameters
3. Type mismatches
4. Resource errors

## Implementation Guidelines

When implementing a new tool:

1. Inherit from `BaseTool`
2. Implement required abstract methods
3. Add comprehensive input validation
4. Include error handling
5. Document all parameters and return values
