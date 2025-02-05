# Welcome to Bedrock Swarm

Bedrock Swarm is a powerful framework for building multi-agent systems using AWS Bedrock. It provides a simple yet flexible API for creating and managing AI agents powered by various AWS Bedrock models.

## Key Features

- **Easy Agent Creation**: Create AI agents with just a few lines of code
- **AWS Bedrock Integration**: Native support for AWS Bedrock models
- **Multi-Agent Support**: Build complex systems with multiple cooperating agents
- **Extensible Tools**: Add custom capabilities to your agents
- **Memory Management**: Built-in conversation memory management
- **Async Support**: Handle concurrent operations efficiently

## Quick Start

```python
from bedrock_swarm import Agent

async def main():
    # Create an agent
    agent = Agent(
        name="assistant",
        model_id="anthropic.claude-v2"
    )
    
    # Have a conversation
    response = await agent.run("Hello! Can you help me with a task?")
    print(response)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

## Installation

Install Bedrock Swarm using pip:

```bash
pip install bedrock-swarm
```

For development:

```bash
pip install bedrock-swarm[dev]
```

For documentation:

```bash
pip install bedrock-swarm[docs]
```

## Next Steps

- Check out the [Quick Start Guide](getting-started/quickstart.md) for a more detailed introduction
- Learn about the core concepts in the [User Guide](user-guide/core-concepts.md)
- Browse the [API Reference](api/agents.md) for detailed documentation
- See [Examples](examples/basic.md) for practical use cases

## Documentation

- [Getting Started](getting-started/installation.md)
- [User Guide](user-guide/core-concepts.md)
- [API Reference](api/agents.md)
- [Examples](examples/basic.md)

## Contributing

We welcome contributions! Please see our [Contributing Guide](contributing.md) for details. 