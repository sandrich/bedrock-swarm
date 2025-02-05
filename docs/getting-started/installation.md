# Installation Guide

## Prerequisites

1. Python 3.11 or later
2. AWS Account with Bedrock access
3. AWS credentials configured

## Installation Methods

### Using pip

```bash
# Basic installation
pip install bedrock-swarm

# With development tools
pip install "bedrock-swarm[dev]"

# With documentation tools
pip install "bedrock-swarm[docs]"
```

### From Source

```bash
git clone https://github.com/yourusername/bedrock-swarm.git
cd bedrock-swarm
pip install -e .
```

## AWS Configuration

1. Configure AWS credentials:
```bash
aws configure
```

2. Or set environment variables:
```bash
export AWS_ACCESS_KEY_ID="your_access_key"
export AWS_SECRET_ACCESS_KEY="your_secret_key"
export AWS_REGION="us-west-2"
```

## Basic Usage

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

## Features

- Multiple model support (Claude, Titan, Jurassic, Cohere)
- Built-in tools (web search, etc.)
- Multi-agent coordination
- Thread-based conversation management
- Workflow orchestration
- Usage monitoring and statistics
- Error handling and validation

## Next Steps

1. Read the [Quick Start Guide](quickstart.md)
2. Explore [Core Concepts](../user-guide/core-concepts.md)
3. Check out [Examples](../examples/)
