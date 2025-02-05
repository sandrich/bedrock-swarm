# Bedrock Swarm

A powerful framework for building multi-agent systems using AWS Bedrock.

## Features

- 🤖 **Multiple Model Support**
  - Claude 3.5 (latest)
  - Claude 2
  - Titan
  - Jurassic
  - Cohere

- 🛠️ **Built-in Tools**
  - Web search
  - Custom tool support
  - Parameter validation
  - Error handling

- 🧠 **Multi-Agent Coordination**
  - Thread-based conversations
  - Workflow orchestration
  - Agent specialization
  - Result aggregation

- 📊 **Monitoring & Control**
  - Usage statistics
  - Token tracking
  - Thread management
  - Workflow status

- 🔧 **Developer Experience**
  - Clear error messages
  - Type hints
  - Comprehensive documentation
  - Example code

## Quick Start

```python
from bedrock_swarm import BedrockAgent
from bedrock_swarm.config import AWSConfig

def main():
    # Configure AWS
    config = AWSConfig(
        region="us-west-2",
        profile="default"
    )

    # Create an agent
    agent = BedrockAgent(
        name="assistant",
        model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        aws_config=config,
        instructions="You are a helpful AI assistant."
    )

    # Process a message
    response = agent.process_message("Hello! What can you help me with?")
    print(response)

if __name__ == "__main__":
    main()
```

## Installation

```bash
pip install bedrock-swarm
```

## Documentation

- [Installation Guide](getting-started/installation.md)
- [Quick Start Guide](getting-started/quickstart.md)
- [Core Concepts](user-guide/core-concepts.md)
- [API Reference](api/index.md)
- [Examples](examples/index.md)

## Contributing

We welcome contributions! Check out our [Contributing Guide](contributing.md) to get started.
