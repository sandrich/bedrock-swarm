# Multi-Agent Example

This example demonstrates how to use multiple specialists together to solve complex tasks.

## Basic Multi-Agent Setup

```python
from bedrock_swarm.agency import Agency
from bedrock_swarm.agents import BedrockAgent
from bedrock_swarm.tools import CalculatorTool, CurrentTimeTool
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

# Create time expert
time_expert = BedrockAgent(
    name="time_expert",
    model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    tools=[CurrentTimeTool()],
    system_prompt="You are a time and timezone expert."
)

# Create agency with both specialists
agency = Agency(
    specialists=[calculator, time_expert],
    shared_instructions="Work together to solve complex time and math problems."
)

# Example multi-step query
response = agency.process_request("What time will it be 15 * 7 minutes from now in UTC?")
print(f"Response: {response}")
```

## Complex Multi-Agent Interactions

```python
# Example showing step-by-step execution
print("\nDetailed Execution:")
print("1. User Request")
response = agency.process_request("What time will it be 15 * 7 minutes from now in UTC?")

print("\n2. Event Trace")
for event in agency.event_system.get_events():
    print(f"\n[{event['timestamp']}] {event['type']} - Agent: {event['agent_name']}")
    for key, value in event['details'].items():
        print(f"  {key}: {value}")
```

## Custom Multi-Agent System

```python
from typing import Any, Dict
from bedrock_swarm.tools import BaseTool

# Custom tools for each specialist
class DataProcessorTool(BaseTool):
    def __init__(self):
        self._name = "process_data"
        self._description = "Process and transform data"

    def _execute_impl(self, *, data: str, **kwargs) -> str:
        # Implementation
        return f"Processed: {data}"

class AnalyzerTool(BaseTool):
    def __init__(self):
        self._name = "analyze_data"
        self._description = "Analyze processed data"

    def _execute_impl(self, *, data: str, **kwargs) -> str:
        # Implementation
        return f"Analysis: {data}"

# Create specialists
processor = BedrockAgent(
    name="processor",
    model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    tools=[DataProcessorTool()],
    system_prompt="You process raw data into structured format."
)

analyzer = BedrockAgent(
    name="analyzer",
    model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    tools=[AnalyzerTool()],
    system_prompt="You analyze processed data and provide insights."
)

# Create agency with custom specialists
agency = Agency(
    specialists=[processor, analyzer],
    shared_instructions="Work together to process and analyze data."
)

# Example workflow
response = agency.process_request("Process and analyze this data: [1, 2, 3, 4, 5]")
print(f"Response: {response}")
```

## Communication Patterns

### Sequential Processing

```python
# Example of sequential processing
queries = [
    "Calculate 15 * 7 and tell me the time that many minutes from now",
    "What time was it 2 * 24 hours ago?",
    "If each task takes 5 * 3 minutes, what time will it be after 4 tasks?"
]

for query in queries:
    print(f"\nQuery: {query}")
    response = agency.process_request(query)
    print(f"Response: {response}")
```

### Parallel Processing

```python
# Example of parallel processing (if supported)
from concurrent.futures import ThreadPoolExecutor

def process_query(query):
    return agency.process_request(query)

queries = [
    "What is 15 * 7?",
    "What time is it in UTC?",
    "What is 22 / 7?"
]

with ThreadPoolExecutor() as executor:
    futures = [executor.submit(process_query, q) for q in queries]
    results = [f.result() for f in futures]

for query, result in zip(queries, results):
    print(f"\nQuery: {query}")
    print(f"Response: {result}")
```

## Error Handling

```python
def test_multi_agent_errors():
    try:
        # Test invalid multi-step query
        response = agency.process_request(
            "Calculate the sine of pi radians and convert to UTC+invalid"
        )
    except Exception as e:
        print(f"Error: {str(e)}")

        # Check event trace for details
        events = agency.event_system.get_events()
        error_events = [e for e in events if e['type'] == 'error']
        for error in error_events:
            print(f"\nError in {error['agent_name']}:")
            print(f"Details: {error['details']}")
```

## Best Practices

1. **Task Planning**
   - Break complex tasks into steps
   - Identify required specialists
   - Handle dependencies properly

2. **Error Handling**
   - Handle errors at each step
   - Provide clear error context
   - Allow graceful degradation

3. **Communication**
   - Clear message passing
   - Proper result formatting
   - Context preservation

4. **Performance**
   - Optimize task distribution
   - Minimize unnecessary calls
   - Handle timeouts properly
