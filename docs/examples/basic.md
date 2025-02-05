# Basic Usage Examples

This guide provides basic examples of using Bedrock Swarm.

## Simple Conversation

Basic interaction with an agent:

```python
from bedrock_swarm import Agent

async def main():
    # Create an agent
    agent = Agent(
        name="assistant",
        model_id="anthropic.claude-v2"
    )
    
    # Have a conversation
    response = await agent.run("What is artificial intelligence?")
    print(response)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

## Using Tools

Example of an agent using tools:

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

Example of using agent memory:

```python
from bedrock_swarm import Agent

async def main():
    # Create agent with memory
    agent = Agent(
        name="memory_assistant",
        memory_config={"type": "simple"}
    )
    
    # Have a conversation with memory
    await agent.run("My name is Alice")
    await agent.run("What's my name?")  # Agent remembers "Alice"
    
    # View memory contents
    memory = await agent.memory.get_recent(5)
    print(memory)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

## Error Handling

Example of proper error handling:

```python
from bedrock_swarm import Agent
from bedrock_swarm.exceptions import AgentError

async def main():
    try:
        agent = Agent(name="error_handler")
        response = await agent.run("Generate a very long response")
    except AgentError as e:
        print(f"Agent error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

## Configuration

Example of configuring an agent:

```python
from bedrock_swarm import Agent

async def main():
    agent = Agent(
        name="configured_assistant",
        model_id="anthropic.claude-v2",
        max_tokens=2000,
        temperature=0.7,
        system_prompt="You are a helpful AI assistant specialized in Python programming.",
        memory_config={
            "type": "simple",
            "max_items": 50
        }
    )
    
    response = await agent.run("How do I write a Python decorator?")
    print(response)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
``` 