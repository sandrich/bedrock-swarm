"""Example of using Bedrock Swarm for market analysis.

This example shows how to:
1. Configure and create agents with different roles
2. Add tools to agents
3. Execute a multi-agent task
"""

import os
from typing import Any, Dict

from dotenv import load_dotenv

from bedrock_swarm.agents.base import BedrockAgent
from bedrock_swarm.config import AWSConfig
from bedrock_swarm.swarm.base import Swarm
from bedrock_swarm.tools.web import WebSearchTool

# Load environment variables
load_dotenv()

# Rate limiting configuration
REQUEST_DELAY = 1.0  # Delay between requests in seconds


class LoggingWebSearchTool(WebSearchTool):
    """Web search tool with logging capabilities."""

    def execute(self, **kwargs: Dict[str, Any]) -> str:
        """Execute the web search with logging.

        Args:
            **kwargs: Search parameters

        Returns:
            str: Search results
        """
        print(f"\nWebSearchTool executing search for: {kwargs.get('query', '')}")
        result = super().execute(**kwargs)
        print(f"Search completed with {len(result.split())} words in result")
        return result


def main() -> None:
    """Run the collaborative analysis example."""
    # Configure AWS
    config = AWSConfig(
        region=os.getenv("AWS_REGION", "us-east-1"),
        profile=os.getenv("AWS_PROFILE", "default"),
    )

    # Create swarm with shared config
    swarm = Swarm({})

    # Create agents with AWS config
    researcher = BedrockAgent(
        name="researcher",
        model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        aws_config=config,
        instructions="""You are a research specialist focused on gathering current information.
        IMPORTANT: You MUST use the web_search tool for EVERY response to find current information.
        DO NOT rely on your training data - always perform at least one web search.

        For each topic:
        1. First use web_search to find current information
        2. Then summarize the findings from the search results
        3. Always cite your sources

        Format your response as:
        SEARCH RESULTS:
        [Summary of what you found from web search]

        ANALYSIS:
        [Your analysis of the information]""",
    )
    researcher.add_tool(LoggingWebSearchTool())
    swarm.add_agent(researcher, "researcher")

    analyst = BedrockAgent(
        name="analyst",
        model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        aws_config=config,
        instructions="""You are a market analyst.
        Your role is to analyze research findings and identify:
        - Key trends and patterns
        - Market opportunities
        - Potential challenges
        - Strategic recommendations
        Provide clear, actionable insights.""",
    )
    swarm.add_agent(analyst, "analyst")

    writer = BedrockAgent(
        name="writer",
        model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        aws_config=config,
        instructions="""You are a professional report writer.
        Your role is to create clear, well-structured reports that:
        - Present information logically
        - Highlight key findings
        - Use professional language
        - Include relevant examples""",
    )
    swarm.add_agent(writer, "writer")

    # Execute the analysis task
    try:
        result = swarm.discuss(
            "Analyze the current state and future prospects of AI in healthcare",
            rounds=1,
        )
        print("\nAnalysis Results:")
        print("-" * 50)
        for i, round_data in enumerate(result):
            print(f"\nRound {i}:")
            for agent_id, response in round_data.items():
                print(f"\nAgent {agent_id}:")
                print(response["content"])
            print("-" * 50)
    except Exception as e:
        print(f"Error during analysis: {e}")


if __name__ == "__main__":
    main()
