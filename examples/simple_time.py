"""Simple example demonstrating the use of CurrentTimeTool with an agent."""

import os

from dotenv import load_dotenv

from bedrock_swarm.agency.agency import Agency
from bedrock_swarm.config import AWSConfig
from bedrock_swarm.tools.time import CurrentTimeTool

# Load AWS credentials from environment
load_dotenv()


def main() -> None:
    """Run the example."""
    # Create AWS config
    aws_config = AWSConfig(
        region=os.getenv("AWS_REGION", "us-east-1"),
        profile=os.getenv("AWS_PROFILE", "default"),
    )

    # Create agency
    agency = Agency(aws_config=aws_config)

    # Create an agent with the time tool
    agency.add_agent(
        name="time_agent",
        model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        tools=[CurrentTimeTool()],
        instructions="You are a helpful assistant that can tell the current time in different formats and timezones.",
    )

    # Create a thread for conversation
    thread = agency.create_thread("time_agent")

    # Example conversation
    messages = [
        "What time is it now?",
        "What time is it in UTC?",
        "What's the current date in YYYY-MM-DD format?",
        "What day of the week is it in Tokyo?",
    ]

    for message in messages:
        print(f"\nUser: {message}")
        response = agency.execute(thread.thread_id, message)
        print(f"Assistant: {response.content}")


if __name__ == "__main__":
    main()
