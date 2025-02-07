"""Example demonstrating the communication trace in an agency with multiple specialists."""

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

    # Create calculator specialist
    calculator = BedrockAgent(
        name="calculator",
        model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        tools=[CalculatorTool()],
        system_prompt="""You are a mathematical specialist that excels at numerical calculations.
You have access to a calculator tool for precise computations.""",
    )

    # Create time specialist
    time_expert = BedrockAgent(
        name="time_expert",
        model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        tools=[CurrentTimeTool()],
        system_prompt="""You are a time and timezone expert.
You have access to a tool that can provide current time information in any timezone.""",
    )

    # Create agency with specialists and let the coordinator determine the best approach
    agency = Agency(
        specialists=[calculator, time_expert],
        shared_instructions="""You are part of an agency with multiple specialists.""",
    )

    # Example queries that require coordination
    queries = [
        "What time will it be 15 * 7 minutes from now in UTC?",
    ]

    print("\nStarting conversation with event tracing...\n")
    for query in queries:
        print(f"User: {query}")
        response = agency.process_request(query)
        print(f"Assistant: {response}\n")

        # Display the event trace for this query
        print("Event Trace:")
        for event in agency.event_system.get_events():
            print(
                f"[{event['timestamp']}] {event['type']} - Agent: {event['agent_name']}"
            )
            for key, value in event["details"].items():
                print(f"  {key}: {value}")
            print()
        print("-" * 80 + "\n")


# Load environment variables
load_dotenv()

if __name__ == "__main__":
    main()
