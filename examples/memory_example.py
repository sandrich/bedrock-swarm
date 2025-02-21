"""Example demonstrating the memory system in bedrock-swarm.

This example shows how memory and context are automatically managed when using the Agency,
making it simple and transparent for users to maintain conversation context and access history.
"""

import os

from bedrock_swarm.agency import Agency
from bedrock_swarm.agents import BedrockAgent
from bedrock_swarm.config import AWSConfig
from bedrock_swarm.tools.calculator import CalculatorTool
from bedrock_swarm.tools.time import CurrentTimeTool


def main() -> None:
    """Run the memory system example demonstrating conversation context and tool usage."""
    # Set AWS configuration
    AWSConfig.region = os.getenv("AWS_REGION", "us-east-1")
    AWSConfig.profile = os.getenv("AWS_PROFILE")

    # Create an agent with tools
    assistant = BedrockAgent(
        name="assistant",
        model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",  # Using supported model version
        role="A helpful assistant that can tell time and do calculations",
        tools=[CurrentTimeTool(), CalculatorTool()],
    )

    # Create the agency with a dictionary of agents
    agency = Agency(agents={"assistant": assistant})

    print("Starting conversation...")
    print("=" * 50)

    # First interaction - Using time tool
    # Agency automatically creates and manages threads
    response = agency.process_request(
        "What time is it in Tokyo?", agent_name="assistant"
    )
    print("\nUser: What time is it in Tokyo?")
    print(f"Assistant: {response}")

    # Second interaction - Using calculator
    # Agency maintains context automatically
    response = agency.process_request("What is 15% of 85?", agent_name="assistant")
    print("\nUser: What is 15% of 85?")
    print(f"Assistant: {response}")

    # Third interaction - Previous context is automatically maintained
    response = agency.process_request(
        "Can you explain how you calculated that?", agent_name="assistant"
    )
    print("\nUser: Can you explain how you calculated that?")
    print(f"Assistant: {response}")

    # Start a new conversation (optional) - Agency handles thread isolation
    print("\nStarting a new conversation:")
    print("=" * 50)

    # Create a new thread by using a different thread ID
    response = agency.process_request(
        "What was the percentage we calculated earlier?",
        agent_name="assistant",
    )
    print("\nUser: What was the percentage we calculated earlier?")
    print(f"Assistant: {response}")  # Will not have access to previous conversation


if __name__ == "__main__":
    main()
