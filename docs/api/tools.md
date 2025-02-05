# Tools API Reference

## BaseTool

::: bedrock_swarm.tools.base.BaseTool
    options:
      show_root_heading: true
      show_source: true

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
    
    async def execute(self, param1: str, param2: int = 0) -> str:
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

The `WebSearchTool` provides web search capabilities using DuckDuckGo:

```python
from bedrock_swarm.tools import WebSearchTool

# Create and configure tool
search_tool = WebSearchTool()

# Add to agent
agent.add_tool(search_tool)

# Use in queries
response = await agent.process_message(
    "What are the latest developments in quantum computing?"
)
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