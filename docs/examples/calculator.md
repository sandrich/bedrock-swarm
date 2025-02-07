# Calculator Example

This example demonstrates how to use the calculator specialist for mathematical operations.

## Basic Calculator Usage

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
    system_prompt="You are a mathematical specialist that excels at numerical calculations."
)

# Create agency
agency = Agency(specialists=[calculator])

# Example calculations
calculations = [
    "What is 15 * 7?",
    "Calculate 100 / 5",
    "What is 23 + 45?",
    "Compute 2 ** 8"
]

for query in calculations:
    print(f"\nQuery: {query}")
    response = agency.process_request(query)
    print(f"Response: {response}")
```

## Custom Calculator Tool

```python
from bedrock_swarm.tools import BaseTool
from typing import Any, Dict

class AdvancedCalculatorTool(BaseTool):
    def __init__(self):
        self._name = "advanced_calculator"
        self._description = "Perform advanced mathematical calculations"

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
                    "expression": {
                        "type": "string",
                        "description": "Mathematical expression to evaluate"
                    },
                    "precision": {
                        "type": "integer",
                        "description": "Number of decimal places (optional)"
                    }
                },
                "required": ["expression"]
            }
        }

    def _execute_impl(self, *, expression: str, precision: int = 2, **kwargs) -> str:
        try:
            # Only allow safe operations
            allowed = set("0123456789+-*/(). ")
            if not all(c in allowed for c in expression):
                raise ValueError("Invalid characters in expression")

            # Evaluate safely
            result = eval(expression, {"__builtins__": {}})

            # Format with specified precision
            return f"{float(result):.{precision}f}"
        except Exception as e:
            raise ValueError(f"Calculation error: {str(e)}")
```

## Using the Advanced Calculator

```python
# Create specialist with advanced calculator
advanced_calculator = BedrockAgent(
    name="advanced_calculator",
    model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    tools=[AdvancedCalculatorTool()],
    system_prompt="""You are a mathematical specialist that can perform calculations with specified precision.
When asked about precision, use the precision parameter. Otherwise, use default precision of 2 decimal places."""
)

# Create agency
agency = Agency(specialists=[advanced_calculator])

# Example calculations with precision
calculations = [
    "Calculate 22/7 with 5 decimal places",
    "What is 100/3?",  # Uses default precision
    "Compute 2.5 * 3.7 with 3 decimal places"
]

for query in calculations:
    print(f"\nQuery: {query}")
    response = agency.process_request(query)
    print(f"Response: {response}")
```

## Error Handling

```python
def test_calculator_errors():
    # Create agency
    agency = Agency(specialists=[calculator])

    # Test invalid expressions
    invalid_queries = [
        "Calculate 1 + x",  # Invalid variable
        "Evaluate 2 ** 1000",  # Too large
        "Compute sin(30)",  # Unsupported function
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

## Event Tracing

```python
# Process calculation with event tracing
response = agency.process_request("Calculate (15 * 7) + (22 / 2)")

print("\nEvent Trace:")
for event in agency.event_system.get_events():
    print(f"[{event['timestamp']}] {event['type']} - Agent: {event['agent_name']}")
    for key, value in event['details'].items():
        print(f"  {key}: {value}")
    print()
```

## Best Practices

1. **Input Validation**
   - Validate expressions before evaluation
   - Check for unsafe operations
   - Handle edge cases

2. **Error Messages**
   - Provide clear error descriptions
   - Include invalid input details
   - Suggest corrections

3. **Precision Handling**
   - Allow precision specification
   - Use consistent rounding
   - Handle floating-point issues

4. **Security**
   - Restrict allowed operations
   - Prevent code injection
   - Limit computation size
