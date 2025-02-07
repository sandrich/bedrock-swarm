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

## 📚 Documentation

Full documentation is available at [bedrock-swarm.readthedocs.io](https://bedrock-swarm.readthedocs.io/). This includes:

- Getting Started Guide
- Core Concepts
- API Reference
- Examples
- Contributing Guidelines

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
from bedrock_swarm.agency import Agency
from bedrock_swarm.agents import BedrockAgent
from bedrock_swarm.tools.time import CurrentTimeTool

# Create a specialist agent
time_agent = BedrockAgent(
    name="time_agent",
    model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    tools=[CurrentTimeTool()],
    system_prompt="You are a helpful assistant that can tell the current time in different formats and timezones."
)

# Create agency with the specialist
agency = Agency(specialists=[time_agent])

# Process time-related requests
response = agency.process_request("What time is it now?")
print(f"Response: {response}")

response = agency.process_request("What time is it in UTC?")
print(f"Response: {response}")
```

## 🎯 Examples

Check out our [examples directory](examples/) for ready-to-use examples:

1. [Agency Example](examples/agency_example.py) - Basic agency setup and usage
2. [Time Example](examples/time_example.py) - Working with time-related tools
3. [Tool Example](examples/tool_example.py) - Creating and using custom tools
4. [Trace Example](examples/trace_example.py) - Event tracing and monitoring

To run the examples:

1. Install with development dependencies:
```bash
pip install "bedrock-swarm[dev]"
```

2. Set up your AWS credentials:
```bash
export AWS_PROFILE=your-profile
export AWS_REGION=your-region
```

3. Run an example:
```bash
python examples/time_example.py
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

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. Check out our [Contributing Guidelines](CONTRIBUTING.md)
2. Fork the repository
3. Create a new branch (`git checkout -b feature/amazing-feature`)
4. Make your changes
5. Run the tests (`pytest tests/unit -v`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

Make sure to:
- Follow the existing code style (we use `black` and `isort`)
- Add tests for new features
- Update documentation as needed

## 🙏 Special Thanks

This project was inspired by and builds upon the excellent work of:
- [Agency Swarm](https://github.com/VRSEN/agency-swarm) - A pioneering framework for multi-agent systems
- The AWS Bedrock team for providing powerful foundation models
- The open-source community for their invaluable contributions

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2024 Chris Sandrini

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
