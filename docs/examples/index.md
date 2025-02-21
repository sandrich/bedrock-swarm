# Examples

This section provides practical examples of using Bedrock Swarm in different scenarios. Each example demonstrates specific features and best practices.

## Basic Examples

### 1. Calculator Agent

A simple example showing how to create and use a calculator agent:

```python
from bedrock_swarm.agents import BedrockAgent
from bedrock_swarm.tools import CalculatorTool
from bedrock_swarm.agency import Agency

# Create calculator agent
calculator = BedrockAgent(
    name="calculator",
    model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    tools=[CalculatorTool()],
    system_prompt="You are a mathematical specialist."
)

# Create agency
agency = Agency(agents=[calculator])

# Process calculations
queries = [
    "What is 2 + 2?",
    "Calculate 15 * 7",
    "What is 100 / 5?",
    "Compute (23 + 7) * 3"
]

for query in queries:
    print(f"\nUser: {query}")
    response = agency.process_request(query, agent_name="calculator")
    print(f"Assistant: {response}")
```

### 2. Time Expert

Example of an agent handling time-related queries:

```python
from bedrock_swarm.agents import BedrockAgent
from bedrock_swarm.tools import CurrentTimeTool
from bedrock_swarm.agency import Agency

# Create time expert agent
time_expert = BedrockAgent(
    name="time_expert",
    model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    tools=[CurrentTimeTool()],
    system_prompt="""You are a time zone specialist. You can:
    - Convert between time zones
    - Tell current time in any location
    - Calculate time differences"""
)

# Create agency
agency = Agency(agents=[time_expert])

# Process time queries
queries = [
    "What time is it in Tokyo?",
    "What time is it in UTC?",
    "What's the time in PST?",
    "Tell me the current time in ISO format"
]

for query in queries:
    print(f"\nUser: {query}")
    response = agency.process_request(query, agent_name="time_expert")
    print(f"Assistant: {response}")
```

## Agency Examples

### 1. Multi-Agent Agency

Example showing how to create and use an agency with multiple agents:

```python
from bedrock_swarm.agency import Agency
from bedrock_swarm.agents import BedrockAgent
from bedrock_swarm.tools import CalculatorTool, CurrentTimeTool

# Create agents
calculator = BedrockAgent(
    name="calculator",
    tools=[CalculatorTool()],
    system_prompt="You handle calculations."
)

time_expert = BedrockAgent(
    name="time_expert",
    tools=[CurrentTimeTool()],
    system_prompt="You handle time-related queries."
)

# Create agency with communication paths
agency = Agency(
    agents=[calculator, time_expert],
    communication_paths={
        "calculator": ["time_expert"],
        "time_expert": ["calculator"]
    }
)

# Process queries
queries = [
    "What is 15 * 7?",  # Routes to calculator
    "What time is it in Tokyo?",  # Routes to time expert
    # Complex query requiring both agents
    "If it's 3:00 PM in New York, and a meeting lasts 2.5 hours, "
    "what time will it end in Tokyo?"
]

for query in queries:
    print(f"\nUser: {query}")
    # Route to appropriate agent based on query
    agent_name = "calculator" if "calculate" in query.lower() else "time_expert"
    response = agency.process_request(query, agent_name=agent_name)
    print(f"Assistant: {response}")
```

### 2. Agency with Event Tracing

Example demonstrating detailed event tracing:

```python
from bedrock_swarm.agency import Agency
from bedrock_swarm.agents import BedrockAgent
from bedrock_swarm.tools import CalculatorTool

# Create agent
calculator = BedrockAgent(
    name="calculator",
    tools=[CalculatorTool()],
    system_prompt="You handle calculations."
)

# Create agency
agency = Agency(agents=[calculator])

# Process query
query = "What is 15 * 7?"
print(f"User: {query}")
response = agency.process_request(query, agent_name="calculator")
print(f"Assistant: {response}")

# Show event trace
print("\nDetailed Event Trace:")
print("=" * 80)
print(agency.get_event_trace())
```

## Memory Examples

### 1. Shared Memory

Example showing how to use shared memory between agents:

```python
from bedrock_swarm.memory import SimpleMemory
from bedrock_swarm.agency import Agency

# Create shared memory
shared_memory = SimpleMemory()

# Create agency with shared memory
agency = Agency(
    agents=[calculator, time_expert],
    shared_memory=shared_memory,
    communication_paths={
        "calculator": ["time_expert"],
        "time_expert": ["calculator"]
    }
)

# Process queries that build on previous context
queries = [
    "What is 15 * 7?",
    "Add 10 to that result",
    "Multiply the result by 2"
]

for query in queries:
    print(f"\nUser: {query}")
    response = agency.process_request(query, agent_name="calculator")
    print(f"Assistant: {response}")

# Show memory contents
print("\nMemory Contents:")
for msg in shared_memory.get_messages():
    print(f"[{msg.role}] {msg.content}")
```

### 2. Thread Memory

Example of using thread-specific memory:

```python
from bedrock_swarm.memory import SimpleMemory
from bedrock_swarm.agency import Agency

# Create agency with memory
agency = Agency(agents=[calculator])

# Create two separate threads
thread1 = agency.create_thread(agent_name="calculator")
thread2 = agency.create_thread(agent_name="calculator")

# Process queries in different threads
thread1.process_message("What is 15 * 7?")
thread2.process_message("What is 25 + 3?")

# Each thread maintains its own context
print("\nThread 1 Memory:")
for msg in thread1.get_messages():
    print(f"[{msg.role}] {msg.content}")

print("\nThread 2 Memory:")
for msg in thread2.get_messages():
    print(f"[{msg.role}] {msg.content}")
```

## Advanced Examples

### 1. Custom Tool Creation

Example of creating and using a custom tool:

```python
from bedrock_swarm.tools import BaseTool
from typing import Dict, Any

class WeatherTool(BaseTool):
    def __init__(self) -> None:
        self._name = "weather"
        self._description = "Get weather information for a location"

    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name"
                    }
                },
                "required": ["location"]
            }
        }

    def _execute_impl(self, *, location: str) -> str:
        # Implement weather lookup logic
        pass
```
