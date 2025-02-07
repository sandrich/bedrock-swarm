# Configuration Guide

## AWS Configuration

### Environment Variables

```bash
# Required
export AWS_REGION=us-east-1
export AWS_PROFILE=default

# Optional
export AWS_ENDPOINT_URL=https://bedrock-runtime.us-east-1.amazonaws.com
```

### Code Configuration

```python
from bedrock_swarm.config import AWSConfig

# Set AWS configuration
AWSConfig.region = "us-east-1"
AWSConfig.profile = "default"
AWSConfig.endpoint_url = "https://bedrock-runtime.us-east-1.amazonaws.com"  # Optional
```

## Agency Configuration

### Basic Setup

```python
from bedrock_swarm.agency import Agency
from bedrock_swarm.agents import BedrockAgent
from bedrock_swarm.memory import SimpleMemory

# Configure an agent
agent = BedrockAgent(
    name="my_agent",
    model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    system_prompt="You are a helpful assistant.",
    memory=SimpleMemory()  # Optional custom memory
)

# Configure agency
agency = Agency(
    specialists=[agent],
    shared_instructions="Common instructions for all agents",
    shared_memory=SimpleMemory()  # Optional shared memory
)
```

### Model Configuration

Available models:
- `us.anthropic.claude-3-5-sonnet-20241022-v2:0` (Default)
- Additional models as supported by AWS Bedrock

### Memory Configuration

```python
from bedrock_swarm.memory import SimpleMemory

# Configure memory settings
memory = SimpleMemory(
    max_messages=100,  # Maximum messages to retain
    ttl=3600  # Time-to-live in seconds
)
```

### Event System Configuration

```python
# Enable detailed event tracing
agency.event_system.enable_debug_logging = True

# Access event trace
events = agency.event_system.get_events()
```

## Security Best Practices

1. **AWS Credentials**
   - Use IAM roles when possible
   - Rotate access keys regularly
   - Never commit credentials to source control

2. **API Keys**
   - Store sensitive data in environment variables
   - Use AWS Secrets Manager for production

3. **Network Security**
   - Configure appropriate VPC settings
   - Use AWS PrivateLink when available
   - Set up proper security groups

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| AWS_REGION | Yes | None | AWS region for Bedrock |
| AWS_PROFILE | No | default | AWS credential profile |
| AWS_ENDPOINT_URL | No | None | Custom endpoint URL |

## Advanced Configuration

### Custom Tool Configuration

```python
from bedrock_swarm.tools import BaseTool

class CustomTool(BaseTool):
    def __init__(self, config: dict):
        self._name = config.get("name", "custom_tool")
        self._description = config.get("description", "")
        self._config = config

    def _execute_impl(self, **kwargs):
        # Custom implementation
        pass
```

### Logging Configuration

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
``` 