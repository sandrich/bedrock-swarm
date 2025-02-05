# Quick Start Guide

This guide will help you create your first agent using Bedrock Swarm.

## Basic Usage

Here's a simple example of creating and using an agent:

```python
from bedrock_swarm import Agent

async def main():
    # Create an agent
    agent = Agent(
        name="assistant",
        model_id="anthropic.claude-v2",
        system_prompt="You are a helpful AI assistant."
    )
    
    # Have a conversation
    response = await agent.run("What can you help me with?")
    print(response)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

## Using Tools

Agents can use tools to perform actions:

```python
from bedrock_swarm import Agent, Tool

class Calculator(Tool):
    name = "calculator"
    description = "Performs basic arithmetic"
    
    async def run(self, x: float, y: float, operation: str) -> float:
        if operation == "add":
            return x + y
        elif operation == "multiply":
            return x * y
        raise ValueError(f"Unknown operation: {operation}")

async def main():
    # Create agent with tool
    agent = Agent(
        name="math_assistant",
        tools=[Calculator()]
    )
    
    # Use the tool through the agent
    response = await agent.run("What is 5 times 3?")
    print(response)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

## Working with Memory

Agents can maintain context across conversations:

```python
async def main():
    # Create agent with memory
    agent = Agent(
        name="memory_assistant",
        memory_config={"type": "simple"}
    )
    
    # Have a conversation with memory
    await agent.run("My name is Alice")
    await agent.run("What's my name?")  # Agent remembers "Alice"

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

## Next Steps

- Learn about [Core Concepts](../user-guide/core-concepts.md)
- Explore [Advanced Examples](../examples/advanced.md)
- Browse the [API Reference](../api/agents.md) 