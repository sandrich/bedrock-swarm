# Advanced Features

## Multi-Agent Workflows

Bedrock Swarm allows you to create complex workflows with multiple agents working together. Each agent can have its own specialization and tools.

```python
from bedrock_swarm import Workflow, WorkflowStep

workflow = Workflow(
    name="research_workflow",
    steps=[
        WorkflowStep(
            agent="researcher",
            instructions="Research the topic",
            tools=[search_tool],
        ),
        WorkflowStep(
            agent="analyst",
            instructions="Analyze the research",
            input_from=["researcher"],
            requires=["researcher"],
        ),
        WorkflowStep(
            agent="writer",
            instructions="Write report",
            input_from=["researcher", "analyst"],
            requires=["analyst"],
        ),
    ],
)
```

## Custom Tools

You can create custom tools by extending the `BaseTool` class:

```python
from bedrock_swarm.tools.base import BaseTool
from typing import Dict, Any

class CustomTool(BaseTool):
    @property
    def name(self) -> str:
        return "custom_tool"

    @property
    def description(self) -> str:
        return "Description of what your tool does"

    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "param1": {"type": "string"},
                    "param2": {"type": "integer"},
                },
                "required": ["param1"],
            },
        }

    def _execute_impl(self, **kwargs: Any) -> str:
        # Implement your tool logic here
        return "Tool result"
```

## Thread Management

Threads allow you to maintain conversation context across multiple interactions:

```python
from bedrock_swarm import Thread

thread = Thread()
thread.add_message("user", "What's the weather like?")
thread.add_message("assistant", "It's sunny today!")

# Later in the conversation
thread.add_message("user", "What about tomorrow?")
```

## Error Handling

Bedrock Swarm provides comprehensive error handling:

```python
from bedrock_swarm.exceptions import (
    ModelInvokeError,
    ResponseParsingError,
    ToolExecutionError,
)

try:
    response = agent.process_message("Your message")
except ModelInvokeError as e:
    print(f"Error invoking model: {e}")
except ResponseParsingError as e:
    print(f"Error parsing response: {e}")
except ToolExecutionError as e:
    print(f"Error executing tool: {e}")
```

## Token Tracking

Monitor token usage across your application:

```python
# Get token count from last interaction
token_count = agent.model.last_token_count

# Reset token count
agent.model.reset_token_count()
```
