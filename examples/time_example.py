"""Example demonstrating the use of CurrentTimeTool with an agent."""

import os

from dotenv import load_dotenv

from bedrock_swarm.agency.agency import Agency
from bedrock_swarm.agents.base import BedrockAgent
from bedrock_swarm.config import AWSConfig
from bedrock_swarm.tools.time import CurrentTimeTool


def main() -> None:
    """Run the example."""
    # Set AWS config from environment
    AWSConfig.region = os.getenv("AWS_REGION", "us-east-1")
    AWSConfig.profile = os.getenv("AWS_PROFILE", "default")
    AWSConfig.endpoint_url = os.getenv("AWS_ENDPOINT_URL")

    # Create agent with time tool
    time_expert = BedrockAgent(
        name="time_expert",
        model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        tools=[CurrentTimeTool()],
        system_prompt="You are a helpful assistant that can tell the current time in different formats and timezones.",
    )

    # Create agency with the time expert
    agency = Agency(specialists=[time_expert])

    # Example queries to test different capabilities
    queries = [
        "What time is it now?",
        "What time is it in UTC?",
    ]

    print("\nStarting conversation with event tracing...\n")
    for query in queries:
        print(f"User: {query}")
        response = agency.process_request(query)
        print(f"Assistant: {response}\n")
        
        # # Display the event trace for this query
        # print("Event Trace:")
        # for event in agency.event_system.get_events():
        #     print(f"[{event['timestamp']}] {event['type']} - Agent: {event['agent_name']}")
        #     for key, value in event['details'].items():
        #         print(f"  {key}: {value}")
        #     print()
        # print("-" * 80 + "\n")


# Load environment variables
load_dotenv()

if __name__ == "__main__":
    main()
