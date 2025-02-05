# Quick Start Guide

This guide will help you get started with Bedrock Swarm, a powerful framework for building multi-agent systems using AWS Bedrock.

## Prerequisites

1. AWS Account with Bedrock access
2. Python 3.11 or later
3. AWS credentials configured

## Installation

```bash
# Basic installation
pip install bedrock-swarm

# With development tools
pip install "bedrock-swarm[dev]"

# With documentation tools
pip install "bedrock-swarm[docs]"
```

## Basic Usage

Here's a simple example of creating and using an agent:

```python
from bedrock_swarm import BedrockAgent
from bedrock_swarm.config import AWSConfig

def main():
    # Configure AWS
    config = AWSConfig(
        region="us-east-1",  # Your AWS region
        profile="default"     # Your AWS profile
    )

    # Create an agent
    agent = BedrockAgent(
        name="assistant",
        model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",  # Latest Claude 3.5
        aws_config=config,
        instructions="You are a helpful AI assistant.",
        temperature=0.7,
        max_tokens=1000
    )

    # Process a message
    response = agent.process_message("What can you help me with?")
    print(response)

if __name__ == "__main__":
    main()
```

## Using Tools

Agents can use tools to perform actions. Here's an example using the built-in web search tool:

```python
from bedrock_swarm import BedrockAgent
from bedrock_swarm.tools.web import WebSearchTool

def main():
    # Create agent with web search capability
    agent = BedrockAgent(
        name="researcher",
        model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        aws_config=config,
        instructions="""You are a research assistant.
        Always use the web_search tool to find current information.
        Summarize your findings clearly."""
    )

    # Add web search tool
    agent.add_tool(WebSearchTool())

    # The agent will automatically use the tool when needed
    response = agent.process_message(
        "What are the latest developments in AI safety?"
    )
    print(response)

if __name__ == "__main__":
    main()
```

## Working with Multiple Agents

Create an agency to coordinate multiple agents:

```python
from bedrock_swarm import Agency, BedrockAgent
from bedrock_swarm.tools.web import WebSearchTool

def main():
    # Create agency with shared configuration
    agency = Agency(
        aws_config=config,
        shared_instructions="Work together to analyze information.",
        temperature=0.7,
        max_tokens=1000
    )

    # Add specialized agents
    agency.add_agent(
        name="researcher",
        model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        instructions="You are a research specialist.",
        tools=[WebSearchTool()]
    )

    agency.add_agent(
        name="analyst",
        model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        instructions="You are a data analyst."
    )

    # Create and use threads
    thread = agency.create_thread("researcher")
    response = thread.execute("Research AI safety")
    print(response.content)

    # Create and execute workflows
    workflow_id = agency.create_workflow(
        name="research_workflow",
        steps=[
            {
                "agent": "researcher",
                "instructions": "Research the topic",
                "tools": [WebSearchTool()]
            },
            {
                "agent": "analyst",
                "instructions": "Analyze the findings",
                "input_from": ["step1"]
            }
        ]
    )

    results = agency.execute_workflow(
        workflow_id=workflow_id,
        input_data={"topic": "AI safety"}
    )

    # Monitor usage
    thread_stats = agency.get_stats(thread.thread_id)
    agent_stats = agency.get_agent_stats("researcher")

if __name__ == "__main__":
    main()
```

## Error Handling

Implement proper error handling for robustness:

```python
from bedrock_swarm.exceptions import (
    ModelInvokeError,
    ToolError,
    ResponseParsingError
)

def main():
    try:
        response = agent.process_message("Your query")
        print(response)
    except ModelInvokeError as e:
        print(f"Model error: {e}")
    except ToolError as e:
        print(f"Tool error: {e}")
    except ResponseParsingError as e:
        print(f"Response parsing error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
```

## Next Steps

- Learn about [Core Concepts](../user-guide/core-concepts.md)
- Explore [Advanced Examples](../examples/advanced.md)
- Browse the [API Reference](../api/agents.md)
- Read the [Contributing Guide](../contributing.md)
