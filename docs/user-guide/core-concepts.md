# Core Concepts

Bedrock Swarm is built around several key concepts that work together to create powerful multi-agent systems.

## Agents

Agents are the core building blocks of the system. Each agent is powered by an AWS Bedrock model and can:

- Process messages and generate responses
- Use tools to perform actions
- Maintain conversation memory
- Follow specific instructions
- Handle function calling and tool execution

```python
agent = BedrockAgent(
    name="assistant",
    model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",  # Latest Claude 3.5 model
    aws_config=config,
    instructions="You are a helpful AI assistant.",
    temperature=0.7,
    max_tokens=1000
)
```

### Agent Properties

- `name`: Unique identifier for the agent
- `model_id`: AWS Bedrock model to use (supports Claude, Titan, Jurassic, and Cohere models)
- `instructions`: System prompt/instructions for the agent
- `temperature`: Controls response randomness (0-1)
- `max_tokens`: Maximum response length

### Supported Models

The following model families and versions are supported:

- Anthropic Claude 3.5:
  - `us.anthropic.claude-3-5-sonnet-20241022-v2:0`
- Anthropic Claude:
  - `anthropic.claude-v1`
  - `anthropic.claude-v2`
  - `anthropic.claude-v2:1`
  - `anthropic.claude-instant-v1`
- Amazon Titan:
  - `amazon.titan-text-express-v1`
  - `amazon.titan-text-lite-v1`
- AI21 Jurassic:
  - `ai21.j2-mid-v1`
  - `ai21.j2-ultra-v1`
- Cohere Command:
  - `cohere.command-text-v14`

## Tools

Tools extend agents' capabilities by allowing them to perform specific actions. Tools include built-in validation:

```python
# Built-in tools
agent.add_tool("WebSearchTool")  # DuckDuckGo web search

# Custom tools
class CustomTool(BaseTool):
    @property
    def name(self) -> str:
        return "custom_tool"

    @property
    def description(self) -> str:
        return "Description of what the tool does"

    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "param1": {
                        "type": "string",
                        "description": "First parameter"
                    },
                    "param2": {
                        "type": "integer",
                        "description": "Second parameter",
                        "minimum": 1,
                        "maximum": 10
                    }
                },
                "required": ["param1"]
            }
        }

    def _execute_impl(self, **kwargs) -> str:
        # Tool implementation
        return "Result"
```

### Tool Properties

- `name`: Unique identifier for the tool
- `description`: What the tool does
- `schema`: JSON schema defining parameters and validation rules
- `_execute_impl`: Implementation of the tool's functionality

### Tool Validation

Tools include built-in validation for:
- Required parameters
- Parameter types (string, integer, boolean, array)
- Numeric constraints (minimum, maximum)
- Array constraints (minItems, maxItems)
- Nested object structures

### Function Calling

Agents can use tools through a function calling interface. The agent can:
1. Parse tool schemas and understand available functions
2. Generate valid JSON function calls
3. Handle function results and continue the conversation

Example function call format:
```json
{
    "function": "web_search",
    "parameters": {
        "query": "latest AI developments",
        "num_results": 5
    }
}
```

## Memory

Memory systems allow agents to maintain context across conversations. The library includes a simple memory implementation and supports custom memory systems:

```python
class CustomMemory(BaseMemory):
    def add_message(self, message: Message) -> None:
        # Store message
        pass

    def get_messages(self, limit: Optional[int] = None) -> List[Message]:
        # Retrieve messages with optional limit
        pass

    def clear(self) -> None:
        # Clear memory
        pass
```

### Message Properties

- `role`: Who sent the message (human/assistant/system)
- `content`: The message content
- `timestamp`: When the message was sent
- `tool_calls`: List of tool calls made in the message
- `tool_results`: Results from tool executions
- `metadata`: Additional information

## Agency

Agencies coordinate multiple agents to solve complex tasks. They support both sequential and parallel execution patterns:

```python
# Create agency with shared configuration
agency = Agency(
    memory=SimpleMemory(),  # Shared memory
    max_rounds=3,  # Maximum discussion rounds
    shared_instructions="Common instructions for all agents",
    shared_files=["context.txt"],  # Shared reference files
    temperature=0.7,  # Default temperature
    max_tokens=1000  # Default max tokens
)

# Add agents with specific roles
agency.add_agent(
    name="researcher",
    model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    instructions="You are a research specialist.",
    tools=[WebSearchTool()]
)

# Sequential execution
result = agency.execute(task)

# Multi-round discussion
history = agency.discuss(topic)

# Get execution status and stats
status = agency.get_workflow_status(workflow_id)
stats = agency.get_agent_stats(agent_name)
```

### Agency Features

- Task distribution and workflow management
- Agent coordination and communication
- Result aggregation and state management
- Multi-round discussions with memory
- Execution statistics and monitoring
- Shared context and configuration

## Error Handling

The library provides specific exceptions for different error cases:

```python
try:
    result = agent.process_message(message)
except ModelInvokeError as e:
    # Handle model API errors
    print(f"Model error: {e}")
except ToolError as e:
    # Handle tool-related errors
    print(f"Tool error: {e}")
except ResponseParsingError as e:
    # Handle response parsing errors
    print(f"Parsing error: {e}")
except InvalidModelError as e:
    # Handle invalid model configuration
    print(f"Model config error: {e}")
```

### Common Exceptions

- `ModelInvokeError`: AWS Bedrock API errors
- `ToolError`: Base class for tool-related errors
- `ToolNotFoundError`: Unknown tool requested
- `ToolExecutionError`: Tool execution failed
- `ResponseParsingError`: Invalid model response
- `InvalidModelError`: Invalid model configuration
- `AWSConfigError`: AWS configuration issues

## Best Practices

1. **Agent Design**
   - Give clear, specific instructions
   - Use appropriate temperature settings (0.7 recommended for most cases)
   - Choose the right model for the task (Claude 3.5 for complex tasks)
   - Implement proper error handling
   - Monitor token usage and costs

2. **Tool Implementation**
   - Make tools focused and reusable
   - Provide clear documentation and schemas
   - Use proper parameter validation
   - Handle errors gracefully
   - Test with different parameter combinations

3. **Memory Management**
   - Clear memory when appropriate
   - Consider memory limitations
   - Use metadata for organization
   - Implement custom memory for specific needs
   - Consider persistence requirements

4. **Agency Coordination**
   - Define clear agent roles
   - Break down complex tasks
   - Monitor agent interactions
   - Use shared context effectively
   - Set appropriate round limits
   - Use sequential execution for dependent tasks

## Threads

Threads manage conversations between users and agents. Each thread:

- Has a unique ID
- Maintains message history
- Tracks tool usage
- Supports tool execution and results

```python
# Create a thread with an agent
thread = agency.create_thread(agent_name="researcher")

# Execute a message in the thread
response = thread.execute("What can you tell me about AI safety?")

# Get thread history
history = thread.get_formatted_history()

# Clear thread history
thread.clear_history()
```

### Thread Features
- Message history tracking
- Tool execution state management
- Formatted history retrieval
- Support for tool calls and results
- Metadata storage

## Workflows

Workflows allow you to orchestrate multi-step processes with different agents:

```python
# Create a workflow
workflow_id = agency.create_workflow(
    name="research_workflow",
    steps=[
        {
            "agent": "researcher",
            "instructions": "Research the topic",
            "tools": [WebSearchTool()],
        },
        {
            "agent": "analyst",
            "instructions": "Analyze the findings",
            "input_from": ["step1"],  # Use results from previous step
        },
        {
            "agent": "writer",
            "instructions": "Write a report",
            "input_from": ["step1", "step2"],
        }
    ]
)

# Execute the workflow
results = agency.execute_workflow(
    workflow_id=workflow_id,
    input_data={"topic": "AI safety"}
)

# Get workflow status
status = agency.get_workflow_status(workflow_id)
```

### Workflow Features
- Sequential step execution
- Input/output chaining between steps
- Tool assignment per step
- Progress tracking
- Result aggregation
- Error handling

## Statistics and Monitoring

The agency provides built-in monitoring capabilities:

```python
# Get thread statistics
thread_stats = agency.get_stats(thread_id)
print(f"Messages: {thread_stats['messages']}")
print(f"Tokens: {thread_stats['tokens']}")

# Get agent statistics
agent_stats = agency.get_agent_stats(agent_name)
```

### Monitoring Features
- Message count tracking
- Token usage monitoring
- Per-agent statistics
- Per-thread statistics
- Workflow execution tracking
