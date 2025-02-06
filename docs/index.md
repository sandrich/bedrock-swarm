# Bedrock Swarm

A powerful framework for building multi-agent systems using AWS Bedrock. This library helps you create, coordinate, and manage AI agents powered by state-of-the-art language models from AWS.

## What is Bedrock Swarm?

Bedrock Swarm simplifies the process of building AI applications using AWS Bedrock. Whether you're creating a single AI assistant or orchestrating multiple specialized agents, this framework provides the tools and structure you need.

### Key Benefits

- 🚀 **Easy to Get Started**: From installation to your first AI agent in minutes
- 🔄 **Flexible & Extensible**: Build simple chatbots or complex multi-agent systems
- 🛡️ **Production Ready**: Built-in error handling, monitoring, and best practices
- 💰 **Cost Effective**: Efficient token usage and usage tracking

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

## Documentation Structure

### Getting Started
- [Installation & Setup](getting-started/installation.md) - First steps to get up and running
- [AWS Configuration](getting-started/configuration.md) - Setting up AWS credentials and access
- [Quick Start Guide](getting-started/quickstart.md) - Create your first AI agent

### User Guide
- [Core Concepts](user-guide/core-concepts.md) - Essential concepts and architecture
- [Working with Agents](user-guide/agents.md) - Creating and managing agents
- [Using Tools](user-guide/tools.md) - Extending agent capabilities
- [Memory Systems](user-guide/memory.md) - Managing conversation history
- [Advanced Features](user-guide/advanced.md) - Complex workflows and optimization
- [Logging & Monitoring](user-guide/logging.md) - Track usage and debug issues

### Examples & Tutorials
- [Basic Examples](examples/basic.md) - Simple use cases to get started
- [Advanced Examples](examples/advanced.md) - Complex multi-agent scenarios
- [Example Gallery](examples/README.md) - Complete project examples

### API Reference
- [Agents API](api/agents.md) - Agent configuration and methods
- [Tools API](api/tools.md) - Built-in and custom tools
- [Memory API](api/memory.md) - Memory system interfaces

## Contributing

We welcome contributions! Please see our [Contributing Guide](contributing.md) for details on:
- Setting up your development environment
- Code style and guidelines
- Submitting pull requests
- Reporting issues

## Support

- [GitHub Issues](https://github.com/yourusername/bedrock-swarm/issues) - Bug reports and feature requests
- [Stack Overflow](https://stackoverflow.com/questions/tagged/bedrock-swarm) - Technical questions
- [Discord Community](https://discord.gg/bedrock-swarm) - Discussion and help

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/yourusername/bedrock-swarm/blob/main/LICENSE) file for details.
