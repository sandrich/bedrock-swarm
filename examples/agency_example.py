"""Example demonstrating the simplified agency implementation."""

import logging
import os

from dotenv import load_dotenv

from bedrock_swarm.agency.agency import Agency
from bedrock_swarm.agents.base import BedrockAgent
from bedrock_swarm.config import AWSConfig
from bedrock_swarm.tools.calculator import CalculatorTool
from bedrock_swarm.tools.time import CurrentTimeTool

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Changed to INFO to reduce noise
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def print_event_trace(agency: Agency, query: str) -> None:
    """Print the event trace for a query."""
    print("\nEvent Trace:")
    print("-" * 40)
    events = agency.event_system.get_events()
    for event in events:
        event_type = event.get("type", "unknown")
        agent_name = event.get("agent_name", "unknown")
        details = event.get("details", {})

        if event_type == "agent_start":
            print(
                f"🟢 Agent {agent_name} started processing: {details.get('message', '')}"
            )
        elif event_type == "tool_start":
            print(
                f"🔧 Tool {details.get('tool_name')} called with args: {details.get('arguments', '')}"
            )
        elif event_type == "tool_complete":
            print(
                f"✅ Tool {details.get('tool_name')} returned: {details.get('result', '')}"
            )
        elif event_type == "tool_error":
            print(
                f"❌ Tool {details.get('tool_name')} error: {details.get('error', '')}"
            )
        elif event_type == "agent_complete":
            print(
                f"🏁 Agent {agent_name} completed with response: {details.get('response', '')}"
            )
        elif event_type == "error":
            print(f"💥 Error: {details.get('error', '')}")
    print("-" * 40)


def setup_aws_config() -> None:
    """Set up AWS configuration from environment variables."""
    required_vars = ["AWS_REGION", "AWS_PROFILE"]
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing)}"
        )

    AWSConfig.region = os.getenv("AWS_REGION")
    AWSConfig.profile = os.getenv("AWS_PROFILE")
    AWSConfig.endpoint_url = os.getenv(
        "AWS_ENDPOINT_URL", f"https://bedrock-runtime.{AWSConfig.region}.amazonaws.com"
    )
    logger.debug(
        f"AWS Config - Region: {AWSConfig.region}, Profile: {AWSConfig.profile}"
    )


def create_agency() -> Agency:
    """Create and configure the agency with specialist agents."""
    logger.debug("Creating specialist agents...")

    # Create calculator agent
    calculator = BedrockAgent(
        name="calculator",
        model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        role="Mathematical calculations and numerical operations",
        tools=[CalculatorTool()],
        system_prompt="You are a specialist that handles calculations and mathematical operations.",
    )

    # Create time expert agent
    time_expert = BedrockAgent(
        name="time_expert",
        model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        role="Time-related operations and timezone conversions",
        tools=[CurrentTimeTool()],
        system_prompt="You are a specialist that handles time-related queries and timezone conversions.",
    )

    # Create agency with specialists
    agency = Agency(agents={"calculator": calculator, "time_expert": time_expert})

    return agency


def main() -> None:
    """Run the example."""
    try:
        # Load environment variables
        load_dotenv()

        # Set up AWS configuration
        setup_aws_config()

        # Create agency
        agency = create_agency()

        # Example queries to test different capabilities
        queries = [
            ("time_expert", "What time is it in Tokyo?"),
            ("calculator", "What is 15 * 7?"),
            ("time_expert", "What time will it be in 3 hours?"),
        ]

        print("\nStarting conversation with agency...\n")
        for agent_name, query in queries:
            try:
                print(f"\nUser: {query}")
                response = agency.process_request(query, agent_name)
                print(f"Assistant: {response}")
                print_event_trace(agency, query)
            except Exception as e:
                logger.error(
                    f"Error processing query '{query}' with agent '{agent_name}': {str(e)}"
                )
                print(f"Error: {str(e)}\n")

    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        raise


if __name__ == "__main__":
    main()
