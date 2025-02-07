# Coordinator

The Coordinator is a specialized agent that manages task planning and delegation within the Bedrock Swarm system.

## Role and Responsibilities

The Coordinator:
1. Receives user requests
2. Creates structured execution plans
3. Delegates tasks to appropriate specialists
4. Manages dependencies between steps
5. Formats final responses

## Plan Creation

### Plan Structure

```json
{
  "steps": [
    {
      "step_number": 1,
      "description": "Calculate 15 * 7",
      "specialist": "calculator"
    },
    {
      "step_number": 2,
      "description": "Calculate time {MINUTES} minutes from now",
      "specialist": "time_expert",
      "requires_results_from": [1]
    }
  ],
  "final_output_format": "In {MINUTES} minutes, it will be {TIME}"
}
```

### Plan Validation

The Coordinator validates:
- Step numbering is sequential
- Dependencies are valid
- Specialists exist
- Steps are atomic
- Descriptions are clear

## Task Delegation

1. **Specialist Selection**
   - Matches tasks to specialist capabilities
   - Ensures specialists have required tools
   - Handles missing specialist errors

2. **Dependency Management**
   - Tracks step dependencies
   - Ensures prerequisites are met
   - Passes results between steps

3. **Error Handling**
   - Validates specialist responses
   - Manages execution failures
   - Provides clear error messages

## Response Formatting

The Coordinator:
1. Collects results from all steps
2. Applies the specified format
3. Creates natural language responses
4. Maintains conversation context

## Example Usage

```python
from bedrock_swarm.agency import Agency
from bedrock_swarm.agents import BedrockAgent
from bedrock_swarm.tools import CalculatorTool, CurrentTimeTool

# Create specialists
calculator = BedrockAgent(
    name="calculator",
    model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    tools=[CalculatorTool()]
)

time_expert = BedrockAgent(
    name="time_expert",
    model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    tools=[CurrentTimeTool()]
)

# Create agency (coordinator is created automatically)
agency = Agency(specialists=[calculator, time_expert])

# Process request (coordinator handles planning)
response = agency.process_request("What time will it be 15 * 7 minutes from now?")
```

## Best Practices

1. **Plan Design**
   - Keep steps atomic
   - Use clear descriptions
   - Specify dependencies explicitly

2. **Specialist Management**
   - Define clear specialist roles
   - Provide focused tools
   - Handle missing specialists

3. **Error Handling**
   - Validate inputs thoroughly
   - Provide helpful error messages
   - Handle edge cases gracefully

4. **Response Formatting**
   - Use clear format templates
   - Include all relevant information
   - Maintain natural language flow
