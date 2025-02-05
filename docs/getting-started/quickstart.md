# Quick Start Guide

This guide will help you get started with Bedrock Swarm by creating a simple multi-agent system.

## Basic Usage

```python
import asyncio
from bedrock_swarm import BedrockAgent
from bedrock_swarm.config import AWSConfig

async def main():
    # Configure AWS
    config = AWSConfig(region="us-west-2")

    # Create an agent
    agent = BedrockAgent(
        name="assistant",
        model_id="anthropic.claude-v2",
        aws_config=config,
        instructions="You are a helpful AI assistant."
    )

    # Process a message
    response = await agent.process_message("What is AWS Bedrock?")
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
```

## Adding Tools

Agents can be enhanced with tools for additional capabilities:

```python
# Add web search capability
agent.add_tool("WebSearchTool")

# Process a message that might use the tool
response = await agent.process_message(
    "What are the latest developments in quantum computing?"
)
```

## Creating a Multi-Agent System

```python
from bedrock_swarm import Agency

# Create specialized agents
researcher = BedrockAgent(
    name="researcher",
    model_id="anthropic.claude-v2",
    aws_config=config,
    instructions="You are a researcher focused on gathering information."
)
researcher.add_tool("WebSearchTool")

analyst = BedrockAgent(
    name="analyst",
    model_id="anthropic.claude-v2",
    aws_config=config,
    instructions="You are an analyst who evaluates and summarizes information."
)

# Create an agency
agency = Agency([researcher, analyst])

# Execute a task
result = await agency.execute(
    "Research and analyze the impact of AI on healthcare"
)
```

## Using Memory

Agents can maintain conversation history:

```python
from bedrock_swarm.memory import SimpleMemory

# Create an agent with memory
agent = BedrockAgent(
    name="assistant",
    model_id="anthropic.claude-v2",
    aws_config=config,
    memory=SimpleMemory()
)

# Messages will be stored in memory
await agent.process_message("Hello!")
await agent.process_message("What did I say before?")
```

## Next Steps

- Learn about [Core Concepts](../user-guide/core-concepts.md)
- Explore [Advanced Patterns](../examples/advanced.md)
- Read the [API Reference](../api/agents.md) 