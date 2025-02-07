"""Example demonstrating the MVP agency implementation with detailed tracing."""

import os

from dotenv import load_dotenv

from bedrock_swarm.agency.agency import Agency
from bedrock_swarm.agents.base import BedrockAgent
from bedrock_swarm.config import AWSConfig
from bedrock_swarm.tools.calculator import CalculatorTool
from bedrock_swarm.tools.time import CurrentTimeTool


def main() -> None:
    """Run the example."""
    # Set AWS config from environment
    AWSConfig.region = os.getenv("AWS_REGION", "us-east-1")
    AWSConfig.profile = os.getenv("AWS_PROFILE", "default")
    AWSConfig.endpoint_url = os.getenv("AWS_ENDPOINT_URL")

    # Create specialist agents
    calculator = BedrockAgent(
        name="calculator",
        model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        tools=[CalculatorTool()],
        system_prompt="You are a specialist that handles calculations and mathematical operations.",
    )

    time_expert = BedrockAgent(
        name="time_expert",
        model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        tools=[CurrentTimeTool()],
        system_prompt="You are a specialist that handles time-related queries and timezone conversions.",
    )

    # Create agency with specialists
    agency = Agency(specialists=[calculator, time_expert])

    # Example queries to test different capabilities
    queries = [
        "What is 15 * 7?",  # Should route to calculator
        "What time is it in Tokyo?",  # Should route to time expert
    ]

    print("\nStarting conversation with agency...\n")
    for query in queries:
        print(f"User: {query}")
        response = agency.get_completion(query)
        print(f"Assistant: {response}\n")


# Load environment variables
load_dotenv()

if __name__ == "__main__":
    main()
