# Time Expert Example

This example demonstrates how to use the time expert specialist for handling time-related queries.

## Basic Time Queries

```python
from bedrock_swarm.agency import Agency
from bedrock_swarm.agents import BedrockAgent
from bedrock_swarm.tools import CurrentTimeTool
from bedrock_swarm.config import AWSConfig

# Configure AWS
AWSConfig.region = "us-east-1"
AWSConfig.profile = "default"

# Create time expert
time_expert = BedrockAgent(
    name="time_expert",
    model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    tools=[CurrentTimeTool()],
    system_prompt="You are a time and timezone expert."
)

# Create agency
agency = Agency(specialists=[time_expert])

# Example time queries
queries = [
    "What time is it now?",
    "What time is it in UTC?",
    "What's the current time in Tokyo?",
    "What time is it in PST?"
]

for query in queries:
    print(f"\nQuery: {query}")
    response = agency.process_request(query)
    print(f"Response: {response}")
```

## Time Calculations

```python
from bedrock_swarm.tools import CalculatorTool

# Create calculator specialist
calculator = BedrockAgent(
    name="calculator",
    model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    tools=[CalculatorTool()],
    system_prompt="You are a mathematical specialist."
)

# Create agency with both specialists
agency = Agency(specialists=[calculator, time_expert])

# Example time calculations
calculations = [
    "What time will it be 30 minutes from now?",
    "What time was it 2 hours ago?",
    "What time will it be 15 * 7 minutes from now in UTC?"
]

for query in calculations:
    print(f"\nQuery: {query}")
    response = agency.process_request(query)
    print(f"Response: {response}")
```

## Custom Time Tool

```python
from bedrock_swarm.tools import BaseTool
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from zoneinfo import ZoneInfo

class AdvancedTimeTool(BaseTool):
    def __init__(self):
        self._name = "advanced_time"
        self._description = "Get current time with advanced formatting options"

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "timezone": {
                        "type": "string",
                        "description": "Timezone name (e.g., 'UTC', 'America/New_York')"
                    },
                    "format": {
                        "type": "string",
                        "description": "Time format (e.g., '%Y-%m-%d %H:%M:%S')"
                    },
                    "offset_minutes": {
                        "type": "integer",
                        "description": "Minutes to add/subtract from current time"
                    }
                },
                "required": ["timezone"]
            }
        }

    def _execute_impl(
        self,
        *,
        timezone: str,
        format: str = "%Y-%m-%d %H:%M:%S %Z",
        offset_minutes: Optional[int] = None,
        **kwargs
    ) -> str:
        try:
            # Get current time in specified timezone
            tz = ZoneInfo(timezone)
            current = datetime.now(tz)

            # Apply offset if specified
            if offset_minutes is not None:
                current += timedelta(minutes=offset_minutes)

            # Format the time
            return current.strftime(format)
        except Exception as e:
            raise ValueError(f"Time operation failed: {str(e)}")
```

## Using the Advanced Time Tool

```python
# Create specialist with advanced time tool
advanced_time = BedrockAgent(
    name="advanced_time",
    model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    tools=[AdvancedTimeTool()],
    system_prompt="""You are a time expert that can:
1. Get current time in any timezone
2. Format time in various ways
3. Calculate future and past times"""
)

# Create agency
agency = Agency(specialists=[advanced_time])

# Example advanced queries
queries = [
    "Show the current time in Tokyo in YYYY-MM-DD HH:mm:ss format",
    "What will the time be in New York 45 minutes from now?",
    "Show today's date in UTC"
]

for query in queries:
    print(f"\nQuery: {query}")
    response = agency.process_request(query)
    print(f"Response: {response}")
```

## Error Handling

```python
def test_time_errors():
    # Create agency
    agency = Agency(specialists=[time_expert])

    # Test invalid queries
    invalid_queries = [
        "What time is it in InvalidZone?",  # Invalid timezone
        "What time will it be 999999 minutes from now?",  # Too large offset
        "What time is it on Mars?"  # Unsupported timezone
    ]

    for query in invalid_queries:
        try:
            response = agency.process_request(query)
            print(f"Query: {query}")
            print(f"Response: {response}")
        except Exception as e:
            print(f"Query: {query}")
            print(f"Error: {str(e)}")
```

## Best Practices

1. **Timezone Handling**
   - Use IANA timezone names
   - Handle common timezone aliases
   - Validate timezone inputs

2. **Time Formatting**
   - Use standard format strings
   - Support various formats
   - Handle localization

3. **Offset Calculations**
   - Validate offset ranges
   - Handle DST transitions
   - Consider timezone changes

4. **Error Handling**
   - Validate all inputs
   - Provide clear error messages
   - Handle edge cases
