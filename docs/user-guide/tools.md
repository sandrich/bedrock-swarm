# Working with Tools

Tools allow agents to interact with external systems and perform specific actions.

## Built-in Tools

Bedrock Swarm comes with several built-in tools:

### Web Search

```python
from bedrock_swarm.tools import WebSearch

agent = Agent(
    tools=[WebSearch()]
)
```

### File Operations

```python
from bedrock_swarm.tools import FileReader, FileWriter

agent = Agent(
    tools=[
        FileReader(),
        FileWriter()
    ]
)
```

## Creating Custom Tools

You can create your own tools by subclassing the `Tool` class:

```python
from bedrock_swarm import Tool

class Calculator(Tool):
    name = "calculator"
    description = "Performs basic arithmetic operations"
    
    async def run(self, operation: str, x: float, y: float) -> float:
        if operation == "add":
            return x + y
        elif operation == "multiply":
            return x * y
        # ... other operations
```

## Tool Parameters

Tools can specify their parameters using type hints:

```python
from typing import List, Optional

class DataAnalyzer(Tool):
    name = "data_analyzer"
    description = "Analyzes numerical data"
    
    async def run(
        self,
        data: List[float],
        operation: str = "mean",
        confidence: Optional[float] = None
    ) -> float:
        # Implementation
        pass
```

## Tool Validation

Implement validation in your tools:

```python
class SafeFileWriter(Tool):
    async def run(self, path: str, content: str) -> bool:
        if not path.endswith('.txt'):
            raise ValueError("Only .txt files are allowed")
        # Implementation
        return True
```

## Using Tools in Agents

Tools can be used individually or in combination:

```python
# Single tool
calculator = Calculator()
result = await calculator.run("add", 2, 3)

# Multiple tools in an agent
agent = Agent(
    tools=[
        Calculator(),
        DataAnalyzer(),
        WebSearch()
    ]
)
```

## Best Practices

1. Keep tool descriptions clear and specific
2. Implement proper error handling
3. Use type hints for better code clarity
4. Document tool parameters and return values
5. Consider security implications when creating tools 