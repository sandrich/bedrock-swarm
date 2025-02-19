"""Integration tests for agency functionality."""

import os
from datetime import datetime

import pytest

from bedrock_swarm.agency.agency import Agency
from bedrock_swarm.agents.base import BedrockAgent
from bedrock_swarm.config import AWSConfig
from bedrock_swarm.tools.calculator import CalculatorTool
from bedrock_swarm.tools.time import CurrentTimeTool


@pytest.fixture
def aws_config():
    """Configure AWS settings for tests."""
    AWSConfig.region = os.getenv("AWS_REGION", "us-east-1")
    AWSConfig.profile = os.getenv("AWS_PROFILE", "default")


@pytest.fixture
def agency(aws_config):
    """Create an agency with calculator and time expert agents."""
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

    return Agency(specialists=[calculator, time_expert])


def test_agency_integration(agency):
    """Test agency with different types of queries."""
    # Test calculator functionality
    calc_response = agency.get_completion("What is 15 * 7?")
    assert (
        "105" in calc_response
    ), "Calculator should return correct multiplication result"

    # Test time functionality with explicit timezone
    time_response = agency.get_completion("What time is it in Tokyo?")
    # Extract time from response and verify format
    try:
        # Response might contain natural language, try to find a time string
        time_formats = [
            "%H:%M:%S",  # 14:30:00
            "%I:%M %p",  # 2:30 PM
            "%I:%M:%S %p",  # 2:30:00 PM
            "%H:%M",  # 14:30
        ]
        dt = None
        for word in time_response.split():
            for fmt in time_formats:
                try:
                    dt = datetime.strptime(word, fmt)
                    break
                except ValueError:
                    continue
            if dt is not None:
                break
        assert dt is not None, "Response should contain a valid time"
    except Exception as e:
        pytest.fail(
            f"Could not parse time from response: {time_response}. Error: {str(e)}"
        )

    # Test combined query
    combined_response = agency.get_completion(
        "What will be the result of 25 * 4 three hours from now?"
    )
    assert "100" in combined_response, "Response should include calculation result"
    assert any(
        time_indicator in combined_response.lower()
        for time_indicator in ["hour", "time", "pm", "am"]
    ), "Response should include time reference"
