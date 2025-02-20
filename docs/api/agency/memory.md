# Memory System

The Memory System in Bedrock Swarm provides context management and message history for agents. It enables agents to maintain state and recall previous interactions.

## BaseMemory

::: bedrock_swarm.memory.base.BaseMemory

## SimpleMemory

::: bedrock_swarm.memory.base.SimpleMemory

## Message

::: bedrock_swarm.memory.base.Message

## Usage Example

```python
from bedrock_swarm.memory.base import SimpleMemory

# Create a memory instance
memory = SimpleMemory()

# Add messages to memory
memory.add_message("user", "What's the weather like?")
memory.add_message("assistant", "It's sunny today.")

# Get message history
history = memory.get_history()
```

## Best Practices

1. Use `SimpleMemory` for basic message history tracking
2. Extend `BaseMemory` for custom memory implementations
3. Implement message filtering and context window management
4. Consider memory persistence for long-running agents
5. Handle message types consistently across the system
