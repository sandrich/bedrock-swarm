# Configuration

This guide explains how to configure Bedrock Swarm for your use case.

## AWS Configuration

Before using Bedrock Swarm, you need to configure your AWS credentials. There are several ways to do this:

### Environment Variables

```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=your_region
```

### AWS CLI Configuration

If you have the AWS CLI installed, you can run:

```bash
aws configure
```

### Using Configuration File

You can also create a `.env` file in your project root:

```plaintext
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=your_region
```

## Bedrock Model Configuration

You can configure which Bedrock models to use for different agent roles:

```python
from bedrock_swarm import Agent

agent = Agent(
    model_id="anthropic.claude-v2",  # or other Bedrock model IDs
    max_tokens=2000,
    temperature=0.7
)
```

## Advanced Configuration

### Logging

Bedrock Swarm uses Python's built-in logging module. You can configure it like this:

```python
import logging

logging.basicConfig(level=logging.INFO)
```

### Memory Configuration

You can configure how agents store and retrieve information:

```python
from bedrock_swarm import Agent

agent = Agent(
    memory_config={
        "type": "simple",  # or "vectorstore"
        "max_items": 100
    }
)
```
