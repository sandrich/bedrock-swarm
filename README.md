# Bedrock Swarm

A framework for building multi-agent systems using AWS Bedrock.

## Features

- Build complex multi-agent systems using AWS Bedrock models
- Easy-to-use API for agent creation and management
- Built-in support for various AWS Bedrock models
- Extensible tool system for agent capabilities
- Memory management for agent conversations
- Async support for concurrent operations

## Installation

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

## Quick Start

```python
from bedrock_swarm import BedrockAgent, Agency
from bedrock_swarm.config import AWSConfig

# Configure AWS
config = AWSConfig(region="us-west-2")

# Create agents
analyst = BedrockAgent(
    name="analyst",
    model_id="anthropic.claude-v2",
    aws_config=config
)

researcher = BedrockAgent(
    name="researcher",
    model_id="anthropic.claude-v2",
    aws_config=config
)

# Create agency
agency = Agency([analyst, researcher])

# Execute tasks
result = await agency.execute("Analyze this dataset and prepare a report")
```

## Documentation

For full documentation, visit [bedrock-swarm.readthedocs.io](https://bedrock-swarm.readthedocs.io).

## Development

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the environment: `source venv/bin/activate`
4. Install development dependencies: `pip install -e ".[dev,docs]"`
5. Run tests: `pytest`
6. Build docs: `mkdocs serve`

## License

MIT License
