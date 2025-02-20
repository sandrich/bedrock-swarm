# Tools

The Bedrock Swarm framework provides a set of built-in tools that agents can use to perform various tasks. Each tool is designed to be modular, reusable, and easy to integrate into agent workflows.

## Available Tools

### Core Tools

- [Base Tool](base.md): The foundation class for all tools
- [Calculator](calculator.md): Performs mathematical calculations
- [Time](time.md): Handles time-related operations
- [Send Message](send_message.md): Facilitates message sending between agents
- [Validation](validation.md): Provides input validation utilities

## Tool Development

For information on developing custom tools, see the [Tool Development Guide](../../development/tools.md).

## Tool Registry

The framework maintains a central registry of available tools:

```python
TOOL_REGISTRY = {
    "calculator": CalculatorTool,
    "time": TimeTool,
    "send_message": SendMessageTool,
    "validation": ValidationTool
}
```

## Common Features

All tools in the framework share these common features:

1. **Standardized Interface**: Consistent method signatures
2. **Error Handling**: Comprehensive error handling and validation
3. **Documentation**: Detailed documentation and examples
4. **Testing**: Comprehensive test coverage
5. **Type Safety**: Full TypeScript support

## Usage Example

```python
from bedrock_swarm.tools import CalculatorTool

calculator = CalculatorTool()
result = calculator.evaluate("2 + 2")
print(result)  # Output: 4
```

## Tool Configuration

Tools can be configured through:

1. Environment variables
2. Configuration files
3. Runtime parameters

## Error Handling

Tools implement standardized error handling:

1. Input validation
2. Type checking
3. Resource availability checks
4. Error reporting
