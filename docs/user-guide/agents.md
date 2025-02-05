# Working with Agents

This guide explains how to work with agents in Bedrock Swarm.

## Creating an Agent

```python
from bedrock_swarm import Agent

agent = Agent(
    name="assistant",
    model_id="anthropic.claude-v2",
    system_prompt="You are a helpful AI assistant."
)
```

## Agent Types

Bedrock Swarm supports different types of agents:

### Basic Agent

The basic agent is suitable for simple tasks and direct interactions:

```python
agent = Agent(name="basic_agent")
response = await agent.run("What is 2+2?")
```

### Tool-using Agent

Agents can use tools to perform actions:

```python
from bedrock_swarm import Agent, Tool

calculator = Tool(
    name="calculator",
    description="Performs basic arithmetic",
    func=lambda x, y: x + y
)

agent = Agent(
    name="math_agent",
    tools=[calculator]
)
```

### Multi-Agent Systems

You can create systems of multiple agents that work together:

```python
from bedrock_swarm import AgentGroup

agents = AgentGroup([
    Agent(name="researcher"),
    Agent(name="writer"),
    Agent(name="editor")
])

result = await agents.collaborate("Write a research paper about AI")
```

## Agent Memory

Agents can maintain memory of past interactions:

```python
# Agent with memory
agent = Agent(
    name="memory_agent",
    memory_config={"type": "simple"}
)

# Interactions are automatically stored
await agent.run("Remember that my favorite color is blue")
await agent.run("What's my favorite color?")  # Agent remembers blue
```

## Error Handling

Handle potential errors in agent interactions:

```python
try:
    response = await agent.run("Complex task")
except Exception as e:
    print(f"Agent encountered an error: {e}")
```

## Best Practices

1. Always provide clear instructions in the system prompt
2. Use appropriate model settings for your use case
3. Implement proper error handling
4. Monitor agent performance and resource usage
5. Consider rate limits and costs when making many requests
