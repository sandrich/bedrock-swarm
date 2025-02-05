# Installation

This guide will help you get started with Bedrock Swarm.

## Requirements

- Python 3.9 or later
- AWS account with access to Bedrock
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

Before using Bedrock Swarm, you need to configure your AWS credentials. There are several ways to do this:

### Environment Variables

```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=your_region
```

### AWS CLI Configuration

If you have the AWS CLI installed:

```bash
aws configure
```

### Using Configuration File

Create a `.env` file in your project root:

```plaintext
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=your_region
```

## Verify Installation

You can verify your installation by running a simple test:

```python
from bedrock_swarm import Agent

async def main():
    agent = Agent(
        name="test_agent",
        model_id="anthropic.claude-v2"
    )
    
    response = await agent.run("Hello! Are you working correctly?")
    print(response)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

## Next Steps

- Follow our [Quick Start Guide](quickstart.md) to create your first agent
- Learn about [Core Concepts](../user-guide/core-concepts.md)
- Check out the [Basic Examples](../examples/basic.md) 