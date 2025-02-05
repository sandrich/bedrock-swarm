# 🤖 Bedrock Swarm

[![PyPI version](https://badge.fury.io/py/bedrock-swarm.svg)](https://badge.fury.io/py/bedrock-swarm)
[![Python](https://img.shields.io/pypi/pyversions/bedrock-swarm.svg)](https://pypi.org/project/bedrock-swarm/)
[![Documentation Status](https://readthedocs.org/projects/bedrock-swarm/badge/?version=latest)](https://bedrock-swarm.readthedocs.io/en/latest/?badge=latest)
[![Tests](https://github.com/sandrich/bedrock-swarm/actions/workflows/tests.yml/badge.svg)](https://github.com/sandrich/bedrock-swarm/actions/workflows/tests.yml)
[![Coverage](https://codecov.io/gh/sandrich/bedrock-swarm/branch/main/graph/badge.svg)](https://codecov.io/gh/sandrich/bedrock-swarm)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A powerful framework for building multi-agent systems using AWS Bedrock. Create, manage, and orchestrate AI agents powered by state-of-the-art language models.

## ✨ Features

- 🚀 **Easy-to-use API** - Create and manage AI agents with just a few lines of code
- 🤝 **Multi-Agent Support** - Build complex systems with multiple cooperating agents
- 🔧 **Extensible Tools** - Add custom capabilities to your agents
- 💾 **Memory Management** - Built-in conversation memory for persistent context
- ⚡ **Async Support** - Handle concurrent operations efficiently
- 🔒 **Type Safety** - Full type hints and runtime type checking
- 📚 **Comprehensive Documentation** - Detailed guides and API reference

## 🛠️ Installation

```bash
# Basic installation
pip install bedrock-swarm

# With development dependencies
pip install bedrock-swarm[dev]

# With documentation dependencies
pip install bedrock-swarm[docs]
```

## 🚀 Quick Start

```python
from bedrock_swarm import BedrockAgent, Agency
from bedrock_swarm.config import AWSConfig

# Configure AWS
config = AWSConfig(region="us-west-2")

# Create agents
analyst = BedrockAgent(
    name="analyst",
    model_id="anthropic.claude-v2",
    aws_config=config,
    instructions="You are a data analyst specialized in market research."
)

researcher = BedrockAgent(
    name="researcher",
    model_id="anthropic.claude-v2",
    aws_config=config,
    instructions="You are a researcher focused on gathering accurate information."
)

# Add tools to agents
analyst.add_tool("WebSearchTool", api_key="your-api-key")

# Create agency
agency = Agency([analyst, researcher])

# Execute tasks
result = await agency.execute("Analyze recent market trends in AI and prepare a report")
```

## 🎯 Examples

Check out our [examples directory](examples/) for ready-to-use examples:

1. [Simple Market Analysis](examples/simple_analysis.py) - A basic example showing how to:
   - Configure AWS and create agents with different roles
   - Add tools to agents for web search capabilities
   - Execute a multi-agent task to analyze AI in healthcare

To run the examples:

1. Install with development dependencies:
```bash
pip install "bedrock-swarm[dev]"
```

2. Set up your environment variables:
```bash
export AWS_REGION=us-west-2
export AWS_PROFILE=default
```

3. Run an example:
```bash
python examples/simple_analysis.py
```

## 📖 Documentation

For comprehensive documentation, visit [bedrock-swarm.readthedocs.io](https://bedrock-swarm.readthedocs.io/):

- [Installation Guide](https://bedrock-swarm.readthedocs.io/en/latest/getting-started/installation/)
- [Quick Start Guide](https://bedrock-swarm.readthedocs.io/en/latest/getting-started/quickstart/)
- [Core Concepts](https://bedrock-swarm.readthedocs.io/en/latest/user-guide/core-concepts/)
- [API Reference](https://bedrock-swarm.readthedocs.io/en/latest/api/agents/)
- [Examples](https://bedrock-swarm.readthedocs.io/en/latest/examples/basic/)

## 🧪 Development

1. Clone the repository:
```bash
git clone https://github.com/sandrich/bedrock-swarm.git
cd bedrock-swarm
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install development dependencies:
```bash
pip install -e ".[dev,docs]"
```

4. Run tests:
```bash
pytest
```

5. Build documentation:
```bash
mkdocs serve
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- AWS Bedrock team for providing the foundation models
- The open-source community for inspiration and tools

## 📬 Contact

- GitHub Issues: [github.com/sandrich/bedrock-swarm/issues](https://github.com/sandrich/bedrock-swarm/issues)
- Documentation: [bedrock-swarm.readthedocs.io](https://bedrock-swarm.readthedocs.io)
