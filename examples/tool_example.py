"""Example demonstrating the use of a simple calculator tool with an agent."""

import os
from typing import Any, Dict

from dotenv import load_dotenv

from bedrock_swarm.agency.agency import Agency
from bedrock_swarm.agents.base import BedrockAgent
from bedrock_swarm.config import AWSConfig
from bedrock_swarm.tools.base import BaseTool


class CalculatorTool(BaseTool):
    """Simple calculator tool for basic arithmetic."""

    def __init__(
        self,
        name: str = "calculator",
        description: str = "Perform basic arithmetic calculations",
    ) -> None:
        """Initialize the calculator tool.

        Args:
            name: Name of the tool
            description: Description of the tool
        """
        self._name = name
        self._description = description

    @property
    def name(self) -> str:
        """Get tool name."""
        return self._name

    @property
    def description(self) -> str:
        """Get tool description."""
        return self._description

    def get_schema(self) -> Dict[str, Any]:
        """Get JSON schema for the calculator tool."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Arithmetic expression to evaluate (e.g. '2 + 2' or '5 * 3')",
                    }
                },
                "required": ["expression"],
            },
        }

    def _execute_impl(self, *, expression: str, **kwargs: Any) -> str:
        """Execute the calculator.

        Args:
            expression: Arithmetic expression to evaluate

        Returns:
            Result of the calculation

        Raises:
            ValueError: If expression is invalid
        """
        # Only allow basic arithmetic for safety
        allowed = set("0123456789+-*/(). ")
        if not all(c in allowed for c in expression):
            raise ValueError("Invalid characters in expression")

        try:
            # Evaluate the expression safely
            result = eval(expression, {"__builtins__": {}})
            return str(result)
        except Exception as e:
            raise ValueError(f"Invalid expression: {str(e)}")


def main() -> None:
    """Run the example."""
    # Set AWS config from environment
    AWSConfig.region = os.getenv("AWS_REGION", "us-east-1")
    AWSConfig.profile = os.getenv("AWS_PROFILE", "default")
    AWSConfig.endpoint_url = os.getenv("AWS_ENDPOINT_URL")

    # Create agent with calculator tool
    calculator = BedrockAgent(
        name="calculator",
        model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        tools=[CalculatorTool()],
        system_prompt="You are a helpful assistant that can perform basic arithmetic calculations.",
    )

    # Create agency with the calculator agent
    agency = Agency(specialists=[calculator])

    # Example queries to test different capabilities
    queries = [
        "Calculate 15 * 7",
    ]

    print("\nStarting conversation...\n")
    for query in queries:
        print(f"User: {query}")
        response = agency.get_completion(query)
        print(f"Assistant: {response}\n")

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
