# Quick Start Guide

This guide will help you get started with Bedrock Swarm quickly.

## Installation

```bash
pip install bedrock-swarm
```

## AWS Configuration

Set up your AWS credentials:

```bash
export AWS_PROFILE=your-profile
export AWS_REGION=your-region
```

Or configure in your code:

```python
from bedrock_swarm.config import AWSConfig

AWSConfig.region = "us-east-1"
AWSConfig.profile = "default"
```

## Basic Example

Here's a simple example using a calculator specialist:

```python
from bedrock_swarm.agency import Agency
from bedrock_swarm.agents import BedrockAgent
from bedrock_swarm.tools import CalculatorTool

# Create a specialist agent
calculator = BedrockAgent(
    name="calculator",
    model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    tools=[CalculatorTool()],
    system_prompt="You are a mathematical specialist."
)

# Create agency with the specialist
agency = Agency(specialists=[calculator])

# Process a request
response = agency.process_request("What is 15 * 7?")
print(response)
```

## Multi-Agent Example

Here's a more complex example using multiple specialists:

```python
from bedrock_swarm.tools import CalculatorTool, CurrentTimeTool

# Create calculator specialist
calculator = BedrockAgent(
    name="calculator",
    model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    tools=[CalculatorTool()],
    system_prompt="You are a mathematical specialist."
)

# Create time expert
time_expert = BedrockAgent(
    name="time_expert",
    model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    tools=[CurrentTimeTool()],
    system_prompt="You are a time and timezone expert."
)

# Create agency with both specialists
agency = Agency(specialists=[calculator, time_expert])

# Process a complex request
response = agency.process_request("What time will it be 15 * 7 minutes from now?")
print(response)
```

## Event Tracing

Enable event tracing to debug agent interactions:

```python
# Process request with event tracing
response = agency.process_request("What is 15 * 7?")
print("Response:", response)

print("\nEvent Trace:")
for event in agency.event_system.get_events():
    print(f"[{event['timestamp']}] {event['type']} - Agent: {event['agent_name']}")
    for key, value in event['details'].items():
        print(f"  {key}: {value}")
    print()
```

## Next Steps

- Learn about the [architecture](../concepts/architecture.md)
- Explore more [examples](../examples/basic.md)
- Read about [core concepts](../concepts/agency.md) 