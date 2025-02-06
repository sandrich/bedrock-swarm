# 🤖 Bedrock Swarm

[![PyPI version](https://badge.fury.io/py/bedrock-swarm.svg)](https://badge.fury.io/py/bedrock-swarm)
[![Python](https://img.shields.io/pypi/pyversions/bedrock-swarm.svg)](https://pypi.org/project/bedrock-swarm)
[![Documentation Status](https://readthedocs.org/projects/bedrock-swarm/badge/?version=latest)](https://bedrock-swarm.readthedocs.io/en/latest/?badge=latest)
[![Tests](https://github.com/sandrich/bedrock-swarm/actions/workflows/tests.yml/badge.svg)](https://github.com/sandrich/bedrock-swarm/actions/workflows/tests.yml)
[![Coverage](https://codecov.io/gh/sandrich/bedrock-swarm/branch/main/graph/badge.svg)](https://codecov.io/gh/sandrich/bedrock-swarm)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

<div align="center">
  <img src="https://raw.githubusercontent.com/sandrich/bedrock-swarm/main/docs/assets/logo.png" alt="Bedrock Swarm Logo" width="400"/>
</div>

A powerful framework for building multi-agent systems using AWS Bedrock. Create, manage, and orchestrate AI agents powered by state-of-the-art language models.

## ✨ Features

- 🚀 **Easy-to-use API** - Create and manage AI agents with just a few lines of code
- 🤝 **Multi-Agent Support** - Build complex systems with multiple cooperating agents
- 🔧 **Extensible Tool System** - Create and add custom tools to enhance agent capabilities
- 💾 **Memory Management** - Built-in conversation memory for persistent context
- 🔒 **Type Safety** - Full type hints and runtime type checking
- 📚 **Comprehensive Documentation** - Detailed guides and API reference

## 🛠️ Installation

```bash
# Basic installation
pip install bedrock-swarm

# With development dependencies
pip install "bedrock-swarm[dev]"

# With documentation dependencies
pip install "bedrock-swarm[docs]"
```

## 🚀 Quick Start

Here's a simple example using an agent with the built-in CurrentTimeTool:

```python
from bedrock_swarm.agency.agency import Agency
from bedrock_swarm.config import AWSConfig
from bedrock_swarm.tools.time import CurrentTimeTool

# Create AWS config
aws_config = AWSConfig(region="us-east-1")

# Create agency
agency = Agency(aws_config=aws_config)

# Create an agent with the time tool
agent = agency.add_agent(
    name="time_agent",
    model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    tools=[CurrentTimeTool()],
    instructions="You are a helpful assistant that can tell the current time in different formats and timezones.",
)

# Create a thread
thread = agency.create_thread("time_agent")

# Example conversation
messages = [
    "What time is it now?",
    "What time is it in UTC?",
    "What's the current date in YYYY-MM-DD format?",
]

for message in messages:
    response = agency.execute(thread.thread_id, message)
    print(f"User: {message}")
    print(f"Assistant: {response.content}\n")
```

## 🎯 Examples

Check out our [examples directory](examples/) for ready-to-use examples:

1. [Simple Time Example](examples/simple_time.py) - A basic example showing how to:
   - Configure AWS and create an agent
   - Use the CurrentTimeTool for time-related queries
   - Handle different time formats and timezones

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
python examples/simple_time.py
```

## 🛠️ Built-in Tools

### CurrentTimeTool

A versatile tool for getting the current time and date in various formats and timezones:

```python
from bedrock_swarm.tools.time import CurrentTimeTool

time_tool = CurrentTimeTool()

# Get current time in ISO format
current_time = time_tool.execute()  # Returns: "2024-03-14T15:09:26"

# Get time in specific format
formatted_time = time_tool.execute(
    format="%Y-%m-%d %H:%M:%S"
)  # Returns: "2024-03-14 15:09:26"

# Get time in specific timezone
utc_time = time_tool.execute(
    timezone="UTC",
    format="%H:%M:%S"
)  # Returns: "15:09:26"

# Get formatted date in specific timezone
tokyo_date = time_tool.execute(
    timezone="Asia/Tokyo",
    format="%A, %B %d, %Y"
)  # Returns: "Thursday, March 14, 2024"
```
