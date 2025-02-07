# Basic Usage

This guide demonstrates the basic usage of Bedrock Swarm with simple examples.

## Simple Calculator Example

```python
from bedrock_swarm.agency import Agency
from bedrock_swarm.agents import BedrockAgent
from bedrock_swarm.tools import CalculatorTool
from bedrock_swarm.config import AWSConfig

# Configure AWS
AWSConfig.region = "us-east-1"
AWSConfig.profile = "default"

# Create calculator specialist
calculator = BedrockAgent(
    name="calculator",
    model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    tools=[CalculatorTool()],
    system_prompt="You are a mathematical specialist."
)

# Create agency
agency = Agency(specialists=[calculator])

# Process a calculation request
response = agency.process_request("What is 15 * 7?")
print(f"Response: {response}")
```

## Time Query Example

```python
from bedrock_swarm.tools import CurrentTimeTool

# Create time expert
time_expert = BedrockAgent(
    name="time_expert",
    model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    tools=[CurrentTimeTool()],
    system_prompt="You are a time and timezone expert."
)

# Create agency
agency = Agency(specialists=[time_expert])

# Process a time request
response = agency.process_request("What time is it in UTC?")
print(f"Response: {response}")
```

## Multi-Step Example

```python
# Create agency with both specialists
agency = Agency(specialists=[calculator, time_expert])

# Process a complex request
response = agency.process_request("What time will it be 15 * 7 minutes from now?")
print(f"Response: {response}")

# View event trace
print("\nEvent Trace:")
for event in agency.event_system.get_events():
    print(f"[{event['timestamp']}] {event['type']} - Agent: {event['agent_name']}")
    for key, value in event['details'].items():
        print(f"  {key}: {value}")
    print()
```

## Understanding the Output

The response includes:
1. The final answer in natural language
2. Event trace showing:
   - Plan creation by coordinator
   - Step execution by specialists
   - Tool usage details
   - Final response formatting

## Common Patterns

### 1. Single Specialist

```python
# Create and use one specialist
specialist = BedrockAgent(
    name="specialist",
    model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    tools=[CustomTool()],
    system_prompt="Specialist instructions"
)

agency = Agency(specialists=[specialist])
response = agency.process_request("Simple request")
```

### 2. Multiple Specialists

```python
# Create and use multiple specialists
specialists = [
    specialist1,
    specialist2,
    specialist3
]

agency = Agency(specialists=specialists)
response = agency.process_request("Complex request")
```

### 3. With Shared Instructions

```python
# Create agency with shared instructions
agency = Agency(
    specialists=specialists,
    shared_instructions="Common instructions for all specialists"
)
```

### 4. With Event Tracing

```python
# Process request and show events
response = agency.process_request("Request")

# Display events
print("\nEvent Trace:")
for event in agency.event_system.get_events():
    print(f"[{event['timestamp']}] {event['type']} - {event['agent_name']}")
```

## Error Handling

```python
try:
    response = agency.process_request("Request that might fail")
except Exception as e:
    print(f"Error: {str(e)}")
    
    # Check event trace for details
    events = agency.event_system.get_events()
    error_events = [e for e in events if e['type'] == 'error']
    for error in error_events:
        print(f"Error in {error['agent_name']}: {error['details']['error']}")
```

## Next Steps

- Learn about [specialist agents](../concepts/specialists.md)
- Explore [tool creation](../concepts/tools.md)
- Understand [event tracing](../concepts/events.md) 