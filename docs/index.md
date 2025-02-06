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
  - Time operations
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
from bedrock_swarm.tools.time import CurrentTimeTool

# Configure AWS credentials
config = AWSConfig(
    region="us-west-2",
    profile="default"
)

# Create an agent
agent = BedrockAgent(
    name="assistant",
    model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    aws_config=config,
    instructions="You are a helpful assistant that can tell time."
)

# Add tools
agent.add_tool(CurrentTimeTool())

# Process a message
response = agent.process_message(
    "What time is it in UTC?"
)
print(response)
```

## Documentation

- [Installation](getting-started/installation.md)
- [Configuration](getting-started/configuration.md)
- [Basic Usage](getting-started/quickstart.md)
- [Tools API](api/tools.md)
- [Advanced Features](user-guide/advanced.md)
- [Examples](examples/README.md)

## Contributing

We welcome contributions! Please see our [Contributing Guide](contributing.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/yourusername/bedrock-swarm/blob/main/LICENSE) file for details.
