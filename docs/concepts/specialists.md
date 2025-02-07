# Specialists

Specialists are domain-specific agents that handle particular types of tasks within the Bedrock Swarm system.

## Core Concepts

### What is a Specialist?

A specialist is a BedrockAgent configured with:
- Specific domain expertise
- Relevant tools for their domain
- Clear system instructions
- Focused responsibility

## Built-in Specialists

### Calculator Specialist

```python
from bedrock_swarm.agents import BedrockAgent
from bedrock_swarm.tools import CalculatorTool

calculator = BedrockAgent(
    name="calculator",
    model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    tools=[CalculatorTool()],
    system_prompt="You are a mathematical specialist that excels at numerical calculations."
)
```

### Time Expert

```python
from bedrock_swarm.tools import CurrentTimeTool

time_expert = BedrockAgent(
    name="time_expert",
    model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    tools=[CurrentTimeTool()],
    system_prompt="You are a time and timezone expert."
)
```

## Creating Custom Specialists

### Basic Structure

```python
from bedrock_swarm.agents import BedrockAgent
from bedrock_swarm.tools import BaseTool

# Create custom tool
class CustomTool(BaseTool):
    def __init__(self):
        self._name = "custom_tool"
        self._description = "Description of what the tool does"

    def _execute_impl(self, **kwargs):
        # Implementation
        pass

# Create specialist with custom tool
custom_specialist = BedrockAgent(
    name="custom_specialist",
    model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    tools=[CustomTool()],
    system_prompt="Specific instructions for this specialist"
)
```

### Best Practices

1. **Focus and Responsibility**
   - Keep specialists focused on one domain
   - Avoid overlapping responsibilities
   - Clear system instructions

2. **Tool Design**
   - Tools should match specialist's domain
   - Clear tool descriptions
   - Proper error handling

3. **System Prompts**
   - Be specific about capabilities
   - Define clear boundaries
   - Include example interactions

## Integration with Agency

```python
from bedrock_swarm.agency import Agency

# Create specialists
specialists = [calculator, time_expert, custom_specialist]

# Create agency with specialists
agency = Agency(
    specialists=specialists,
    shared_instructions="Common instructions for all specialists"
)
```

## Communication Flow

1. **Request Reception**
   - Coordinator receives user request
   - Creates execution plan
   - Identifies required specialists

2. **Task Execution**
   - Specialist receives task
   - Uses appropriate tools
   - Returns formatted results

3. **Result Integration**
   - Results passed between specialists
   - Dependencies managed
   - Final response formatted

## Error Handling

### Specialist Level

```python
class CustomSpecialist(BedrockAgent):
    def handle_error(self, error):
        """Custom error handling logic"""
        self.log_error(error)
        return f"Error in specialist: {str(error)}"
```

### Tool Level

```python
class CustomTool(BaseTool):
    def _execute_impl(self, **kwargs):
        try:
            # Implementation
            pass
        except Exception as e:
            raise ValueError(f"Tool execution failed: {str(e)}")
```

## Memory Management

Specialists can maintain their own memory:

```python
from bedrock_swarm.memory import SimpleMemory

specialist = BedrockAgent(
    name="specialist",
    model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    memory=SimpleMemory(),  # Specialist-specific memory
    tools=[CustomTool()]
)
```

## Testing Specialists

```python
def test_specialist():
    # Create specialist
    specialist = BedrockAgent(
        name="test_specialist",
        model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        tools=[CustomTool()]
    )
    
    # Test basic functionality
    response = specialist.generate("Test request")
    assert response is not None
    
    # Test tool execution
    tool_response = specialist.tools["custom_tool"].execute(arg="test")
    assert tool_response is not None
``` 