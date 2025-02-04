"""
A simple example demonstrating how to use Bedrock Swarm for market analysis.

This example shows how to:
1. Configure and create agents with different roles
2. Add tools to agents
3. Execute a multi-agent task
"""

import asyncio
import os
from dotenv import load_dotenv

from bedrock_swarm import BedrockAgent, Agency
from bedrock_swarm.config import AWSConfig

# Load environment variables
load_dotenv()

async def main():
    # Configure AWS
    config = AWSConfig(
        region=os.getenv("AWS_REGION", "us-west-2"),
        profile=os.getenv("AWS_PROFILE", "default")
    )

    # Create a market analyst agent
    analyst = BedrockAgent(
        name="market_analyst",
        model_id="anthropic.claude-v2",
        aws_config=config,
        instructions="""You are a market analyst specialized in technology trends.
        Your role is to analyze market data and provide actionable insights.""",
        temperature=0.7
    )

    # Add web search capability to the analyst
    analyst.add_tool("WebSearchTool")  # No API key needed - uses DuckDuckGo

    # Create a report writer agent
    writer = BedrockAgent(
        name="report_writer",
        model_id="anthropic.claude-v2",
        aws_config=config,
        instructions="""You are a professional report writer.
        Your role is to create clear, concise, and well-structured reports
        based on the analysis provided.""",
        temperature=0.3
    )

    # Create an agency with both agents
    agency = Agency([analyst, writer])

    # Define the analysis task
    task = """
    1. Research and analyze the current state of AI in healthcare
    2. Focus on:
       - Major players and their innovations
       - Recent breakthroughs
       - Market size and growth projections
       - Key challenges and opportunities
    3. Prepare a concise report with key findings
    """

    try:
        # Execute the task
        result = await agency.execute(task)
        print("\nAnalysis Report:")
        print("---------------")
        print(result)

    except Exception as e:
        print(f"Error during analysis: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 