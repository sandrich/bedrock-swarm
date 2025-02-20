"""Simple example demonstrating agency usage with specialist agents."""

import os

from dotenv import load_dotenv

from bedrock_swarm.agency.agency import Agency
from bedrock_swarm.agents.base import BedrockAgent
from bedrock_swarm.config import AWSConfig
from bedrock_swarm.tools.calculator import CalculatorTool
from bedrock_swarm.tools.time import CurrentTimeTool

# Load environment variables and configure AWS
load_dotenv()
AWSConfig.region = os.getenv("AWS_REGION", "us-east-1")
AWSConfig.profile = os.getenv("AWS_PROFILE")

# Create specialist agents
calculator = BedrockAgent(
    name="calculator",
    model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    role="Mathematical calculations and numerical operations",
    tools=[CalculatorTool()],
    system_prompt="You are a specialist that handles calculations and mathematical operations.",
)

time_expert = BedrockAgent(
    name="time_expert",
    model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    role="Time-related operations and timezone conversions",
    tools=[CurrentTimeTool()],
    system_prompt="You are a specialist that handles time-related queries and timezone conversions.",
)

# Create agency with specialists
agency = Agency(agents={"calculator": calculator, "time_expert": time_expert})

# Example queries
queries = [
    ("time_expert", "What time is it in Tokyo?"),
    ("calculator", "What is 15 * 7?"),
    ("time_expert", "What time will it be in 3 hours?"),
]

# Process queries
for agent_name, query in queries:
    print(f"\nQuery: {query}")
    response = agency.process_request(query, agent_name)
    print(f"Response: {response}\n")
