# Examples

This section provides practical examples of using Bedrock Swarm in different scenarios. Each example demonstrates specific features and best practices.

## Basic Examples

### 1. Calculator Agent

A simple example showing how to create and use a calculator agent:

```python
from bedrock_swarm.agents.base import BedrockAgent
from bedrock_swarm.tools.calculator import CalculatorTool
from bedrock_swarm.agency.thread import Thread

# Create calculator agent
calculator = BedrockAgent(
    name="calculator",
    model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    tools=[CalculatorTool()],
    system_prompt="You are a specialist that handles calculations."
)

# Create thread
thread = Thread(agent=calculator)

# Process calculations
queries = [
    "What is 2 + 2?",
    "Calculate 15 * 7",
    "What is 100 / 5?",
    "Compute (23 + 7) * 3"
]

for query in queries:
    print(f"\nUser: {query}")
    response = thread.process_message(query)
    print(f"Assistant: {response}")
```

### 2. Time Expert

Example of an agent handling time-related queries:

```python
from bedrock_swarm.agents.base import BedrockAgent
from bedrock_swarm.tools.time import CurrentTimeTool
from bedrock_swarm.agency.thread import Thread

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

# Create thread
thread = Thread(agent=time_expert)

# Process time queries
queries = [
    "What time is it in Tokyo?",
    "What time is it in UTC?",
    "What's the time in PST?",
    "Tell me the current time in ISO format"
]

for query in queries:
    print(f"\nUser: {query}")
    response = thread.process_message(query)
    print(f"Assistant: {response}")
```

## Agency Examples

### 1. Basic Agency

Example showing how to create and use an agency with multiple specialists:

```python
from bedrock_swarm.agency.agency import Agency
from bedrock_swarm.agents.base import BedrockAgent
from bedrock_swarm.tools.calculator import CalculatorTool
from bedrock_swarm.tools.time import CurrentTimeTool

# Create specialists
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

# Create agency
agency = Agency(specialists=[calculator, time_expert])

# Process queries
queries = [
    "What is 15 * 7?",  # Routes to calculator
    "What time is it in Tokyo?",  # Routes to time expert
    # Complex query requiring both specialists
    "If it's 3:00 PM in New York, and a meeting lasts 2.5 hours, "
    "what time will it end in Tokyo?"
]

for query in queries:
    print(f"\nUser: {query}")
    response = agency.get_completion(query)
    print(f"Assistant: {response}")
```

### 2. Agency with Event Tracing

Example demonstrating detailed event tracing:

```python
from bedrock_swarm.agency.agency import Agency
from bedrock_swarm.agents.base import BedrockAgent
from bedrock_swarm.tools.calculator import CalculatorTool

# Create specialist
calculator = BedrockAgent(
    name="calculator",
    tools=[CalculatorTool()],
    system_prompt="You handle calculations."
)

# Create agency
agency = Agency(specialists=[calculator])

# Process query
query = "What is 15 * 7?"
print(f"User: {query}")
response = agency.get_completion(query)
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
from bedrock_swarm.memory.base import SimpleMemory
from bedrock_swarm.agency.agency import Agency

# Create shared memory
shared_memory = SimpleMemory()

# Create agency with shared memory
agency = Agency(
    specialists=[calculator, time_expert],
    shared_memory=shared_memory
)

# Process queries that build on previous context
queries = [
    "What is 15 * 7?",
    "Add 10 to that result",
    "Multiply the result by 2"
]

for query in queries:
    print(f"\nUser: {query}")
    response = agency.get_completion(query)
    print(f"Assistant: {response}")

# Show memory contents
print("\nMemory Contents:")
for msg in shared_memory.get_messages():
    print(f"[{msg.role}] {msg.content}")
```

### 2. Persistent Memory

Example of saving and loading memory state:

```python
from bedrock_swarm.memory.base import PersistentMemory

# Create persistent memory
memory = PersistentMemory()

# Use memory
agency = Agency(
    specialists=[calculator],
    shared_memory=memory
)

# Process some queries
agency.get_completion("What is 15 * 7?")

# Save memory state
memory.save_to_file("agency_memory.json")

# Later, load the memory
loaded_memory = PersistentMemory.load_from_file("agency_memory.json")
new_agency = Agency(
    specialists=[calculator],
    shared_memory=loaded_memory
)
```

## Advanced Examples

### 1. Custom Tool Creation

Example of creating and using a custom tool:

```python
from bedrock_swarm.tools.base import BaseTool

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
        return f"Weather information for {location}"

# Use custom tool
weather_expert = BedrockAgent(
    name="weather_expert",
    tools=[WeatherTool()],
    system_prompt="You provide weather information."
)
```

### 2. Complex Agency Communication

Example of complex inter-agent communication:

```python
from bedrock_swarm.agency.agency import Agency

# Create agency with complex communication paths
agency = Agency(
    agency_chart=[
        coordinator,  # Can talk to user
        [coordinator, researcher],  # Coordinator -> Researcher
        [researcher, summarizer],   # Researcher -> Summarizer
        [summarizer, coordinator],  # Summarizer -> Coordinator
    ]
)

# Process complex query
response = agency.get_completion(
    "Research the impact of AI on healthcare and provide a summary"
)
print(response)

# Show event trace to see communication flow
print(agency.get_event_trace())
```

### 3. Custom Event Analysis

Example of analyzing event patterns:

```python
from bedrock_swarm.events import EventSystem, EventAnalytics

# Create analytics
analytics = EventAnalytics(agency.event_system)

# Get run statistics
stats = analytics.get_run_stats(run_id)
print(f"Total events: {stats['total_events']}")
print(f"Tool executions: {stats['tool_executions']}")
print(f"Errors: {stats['errors']}")
print(f"Duration: {stats['duration']:.2f}s")

# Visualize timeline
visualizer = EventVisualizer(agency.event_system)
timeline = visualizer.generate_timeline(run_id)
print("\nEvent Timeline:")
print(timeline)
```
