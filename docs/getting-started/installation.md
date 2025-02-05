# Installation

## Requirements

- Python 3.9 or higher
- AWS account with Bedrock access
- AWS credentials configured

## Installation Methods

### Using pip

```bash
# Basic installation
pip install bedrock-swarm

# With development dependencies
pip install bedrock-swarm[dev]

# With documentation dependencies
pip install bedrock-swarm[docs]
```

### From Source

```bash
git clone https://github.com/yourusername/bedrock-swarm.git
cd bedrock-swarm
pip install -e ".[dev,docs]"
```

## AWS Configuration

1. Configure your AWS credentials:

```bash
aws configure
```

Or set environment variables:

```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_REGION=us-west-2
```

2. Ensure you have access to AWS Bedrock and the required models:
   - Anthropic Claude (recommended)
   - Amazon Titan
   - AI21 Jurassic
   - Cohere Command

## Verifying Installation

```python
from bedrock_swarm import BedrockAgent
from bedrock_swarm.config import AWSConfig

# Create a config
config = AWSConfig(region="us-west-2")

# Create an agent
agent = BedrockAgent(
    name="test_agent",
    model_id="anthropic.claude-v2",
    aws_config=config
)

# Test the agent
response = await agent.process_message("Hello!")
print(response)
```

## Next Steps

- Follow the [Quick Start Guide](quickstart.md) to create your first agent
- Learn about [Core Concepts](../user-guide/core-concepts.md)
- Check out the [Examples](../examples/basic.md) 