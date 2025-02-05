# Examples

This directory contains example scripts demonstrating how to use Bedrock Swarm in various scenarios.

## Prerequisites

1. Install the package with development dependencies:
```bash
pip install "bedrock-swarm[dev]"
```

2. Set up your environment variables in a `.env` file:
```bash
AWS_REGION=us-west-2
AWS_PROFILE=default
```

## Available Examples

### 1. Simple Market Analysis (`simple_analysis.py`)

A basic example showing how to:
- Configure AWS and create agents with different roles
- Add tools to agents (including web search using DuckDuckGo)
- Execute a multi-agent task for market analysis

To run:
```bash
python simple_analysis.py
```

This example creates two agents:
1. A market analyst that researches and analyzes data using DuckDuckGo search
2. A report writer that formats and presents the findings

The agents work together to analyze the current state of AI in healthcare and produce a structured report.
