# Quick Start Guide

Welcome to Bedrock Swarm! This guide will help you create your first AI agent and understand the basic concepts of the framework.

## Overview

Bedrock Swarm helps you build AI applications using AWS Bedrock. You can:
- Create AI agents powered by state-of-the-art language models
- Add capabilities to agents using tools
- Build multi-agent systems that work together
- Monitor and control agent behavior

## Prerequisites

Before starting, ensure you have:
- Completed the [Installation Guide](installation.md)
- Configured your AWS credentials
- Basic Python knowledge

## Your First Agent

Let's create a simple AI assistant that can help answer questions.

```python
from bedrock_swarm import BedrockAgent
from bedrock_swarm.config import AWSConfig

# 1. Configure AWS settings
config = AWSConfig(
    region="us-west-2",  # Your AWS region
    profile="default"     # Your AWS profile
)

# 2. Create an agent
agent = BedrockAgent(
    name="assistant",                                     # Name for your agent
    model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",  # Using Claude 3.5
    aws_config=config,                                    # AWS configuration
    instructions="You are a helpful AI assistant.",       # Agent's behavior
    temperature=0.7,                                      # Response creativity (0-1)
    max_tokens=1000                                      # Maximum response length
)

# 3. Send a message and get a response
response = agent.process_message("What can you help me with?")
print(response)
```

### Understanding the Code

1. **AWS Configuration**: The `AWSConfig` class manages your AWS credentials and settings
2. **Agent Creation**: `BedrockAgent` is the core class for creating AI agents
3. **Agent Parameters**:
   - `name`: Identifier for your agent
   - `model_id`: The AWS Bedrock model to use
   - `instructions`: Guides the agent's behavior and responses
   - `temperature`: Controls response randomness (0=deterministic, 1=creative)
   - `max_tokens`: Limits response length

## Adding Capabilities with Tools

Agents become more powerful when given tools. Let's create an agent that can tell time:

```python
from bedrock_swarm import BedrockAgent
from bedrock_swarm.tools.time import CurrentTimeTool

# Create agent with time capability
agent = BedrockAgent(
    name="time_assistant",
    model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    aws_config=config,
    instructions="""You are a helpful assistant that can tell time.
    Always use the current_time tool when asked about the current time."""
)

# Add the time tool
agent.add_tool(CurrentTimeTool())

# Ask about the time
response = agent.process_message("What time is it in UTC?")
print(response)

# Ask about multiple time zones
response = agent.process_message("What time is it in New York and London?")
print(response)
```

### Built-in Tools

Bedrock Swarm includes several useful tools:
- `CurrentTimeTool`: Get current time in any timezone
- `WebSearchTool`: Search the internet
- `CalculatorTool`: Perform calculations
- `WeatherTool`: Get weather information

## Working with Memory

Agents can remember conversation history:

```python
# Create agent with memory
agent = BedrockAgent(
    name="memory_assistant",
    model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    aws_config=config,
    instructions="You are a helpful assistant with memory of conversations."
)

# Have a conversation
response1 = agent.process_message("My name is Alice.")
print(response1)

response2 = agent.process_message("What's my name?")
print(response2)  # The agent remembers "Alice"

# Clear memory if needed
agent.clear_memory()
```

## Multi-Agent Systems

Create multiple agents that work together:

```python
from bedrock_swarm import Agency
from bedrock_swarm.tools.web import WebSearchTool

# Create an agency
agency = Agency(
    aws_config=config,
    shared_instructions="Work together to analyze information."
)

# Add specialized agents
agency.add_agent(
    name="researcher",
    model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    instructions="You are a research specialist.",
    tools=[WebSearchTool()]
)

agency.add_agent(
    name="analyst",
    model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    instructions="You analyze and summarize information."
)

# Create a conversation thread
thread = agency.create_thread("researcher")
response = thread.execute("Research recent AI developments")
print(response.content)
```

## Error Handling

Always implement proper error handling in your applications:

```python
from bedrock_swarm.exceptions import ModelInvokeError, ToolError

try:
    response = agent.process_message("Your query")
    print(response)
except ModelInvokeError as e:
    print(f"Model error: {e}")
except ToolError as e:
    print(f"Tool error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Best Practices

1. **Agent Instructions**
   - Be specific about the agent's role and capabilities
   - Include examples of desired behavior
   - Specify how and when to use tools

2. **Tool Usage**
   - Add only the tools an agent needs
   - Provide clear instructions for tool usage
   - Handle tool errors gracefully

3. **Memory Management**
   - Clear memory when starting new conversations
   - Consider memory limits for long conversations
   - Use metadata to organize conversations

4. **Performance**
   - Choose appropriate `max_tokens` values
   - Monitor token usage and costs
   - Use the right model for your task

## Next Steps

1. Explore [Core Concepts](../user-guide/core-concepts.md) for deeper understanding
2. Try the [Basic Examples](../examples/basic.md) for common use cases
3. Learn about [Advanced Features](../user-guide/advanced.md) for complex applications

## Getting Help

- Check [Common Issues](installation.md#common-issues-and-solutions)
- Browse [Example Code](../examples/)
- Join our [Discord Community](https://discord.gg/bedrock-swarm)
