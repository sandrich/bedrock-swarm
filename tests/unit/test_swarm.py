"""Tests for the swarm functionality."""

# mypy: ignore-errors

from typing import Dict
from unittest.mock import MagicMock

import pytest

from bedrock_swarm.agents.base import BedrockAgent
from bedrock_swarm.config import AWSConfig
from bedrock_swarm.memory.base import SimpleMemory
from bedrock_swarm.swarm.base import Swarm


@pytest.fixture
def aws_config() -> Dict[str, str]:
    """Create a mock AWS configuration."""
    return {
        "region_name": "us-west-2",
    }


@pytest.fixture
def mock_agent() -> BedrockAgent:
    """Create a mock Bedrock agent."""
    config = AWSConfig(region="us-west-2", profile="default")
    agent = BedrockAgent(
        name="test_agent",
        model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        instructions="Test instructions",
        aws_config=config,
    )
    agent.memory = SimpleMemory(max_size=5)
    return agent


@pytest.fixture
def swarm(mock_agent: BedrockAgent) -> Swarm:
    """Create a Swarm instance for testing."""
    agents = {}
    swarm = Swarm(agents)
    swarm.add_agent(mock_agent, "test_agent")
    return swarm


def test_init_basic(swarm: Swarm) -> None:
    """Test basic initialization of Swarm."""
    assert isinstance(swarm, Swarm)
    assert len(swarm.agents) == 1


def test_add_agent(swarm: Swarm, mock_agent: BedrockAgent) -> None:
    """Test adding an agent to the swarm."""
    swarm.add_agent(mock_agent, "test_agent_1")
    assert "test_agent_1" in swarm.agents
    assert swarm.agents["test_agent_1"] == mock_agent


def test_get_agent(swarm: Swarm, mock_agent: BedrockAgent) -> None:
    """Test getting an agent from the swarm."""
    retrieved_agent = swarm.get_agent("test_agent")
    assert retrieved_agent == mock_agent


def test_remove_agent(swarm: Swarm, mock_agent: BedrockAgent) -> None:
    """Test removing an agent from the swarm."""
    swarm.remove_agent("test_agent")
    assert "test_agent" not in swarm.agents


def test_get_nonexistent_agent(swarm: Swarm) -> None:
    """Test getting a nonexistent agent from the swarm."""
    with pytest.raises(KeyError):
        swarm.get_agent("nonexistent_agent")


def test_process_message(swarm: Swarm, mock_agent: BedrockAgent) -> None:
    """Test processing a message through the swarm."""
    message = "Test message"
    tool_results = [{"tool": "test_tool", "result": "test_result"}]
    mock_agent.process_message = MagicMock(return_value="Test response")
    response = swarm.process_message("test_agent", message, tool_results=tool_results)
    assert response == "Test response"
    mock_agent.process_message.assert_called_once_with(
        message, tool_results=tool_results
    )
