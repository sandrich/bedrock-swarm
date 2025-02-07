"""Tests for the swarm functionality."""

# mypy: ignore-errors

from typing import Dict
from unittest.mock import MagicMock

import pytest

from bedrock_swarm.agents.base import BedrockAgent
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
    agent = BedrockAgent(
        name="test_agent",
        model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    )
    agent.process_message = MagicMock(return_value="Test response")
    return agent


@pytest.fixture
def mock_agent2() -> BedrockAgent:
    """Create a second mock agent."""
    agent = BedrockAgent(
        name="test_agent2",
        model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    )
    agent.process_message = MagicMock(return_value="Test response 2")
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
    assert len(swarm.history) == 0


def test_add_agent(swarm: Swarm, mock_agent: BedrockAgent) -> None:
    """Test adding an agent to the swarm."""
    swarm.add_agent(mock_agent, "test_agent_1")
    assert "test_agent_1" in swarm.agents
    assert swarm.agents["test_agent_1"] == mock_agent


def test_add_duplicate_agent(swarm: Swarm, mock_agent: BedrockAgent) -> None:
    """Test adding a duplicate agent."""
    with pytest.raises(ValueError, match="Agent 'test_agent' already exists"):
        swarm.add_agent(mock_agent, "test_agent")


def test_get_agent(swarm: Swarm, mock_agent: BedrockAgent) -> None:
    """Test getting an agent from the swarm."""
    retrieved_agent = swarm.get_agent("test_agent")
    assert retrieved_agent == mock_agent


def test_remove_agent(swarm: Swarm, mock_agent: BedrockAgent) -> None:
    """Test removing an agent from the swarm."""
    assert swarm.remove_agent("test_agent")  # Should return True
    assert "test_agent" not in swarm.agents
    assert not swarm.remove_agent(
        "test_agent"
    )  # Should return False when already removed


def test_get_nonexistent_agent(swarm: Swarm) -> None:
    """Test getting a nonexistent agent from the swarm."""
    with pytest.raises(KeyError, match="Agent 'nonexistent_agent' not found"):
        swarm.get_agent("nonexistent_agent")


def test_process_message(swarm: Swarm, mock_agent: BedrockAgent) -> None:
    """Test processing a message through the swarm."""
    message = "Test message"
    tool_results = [{"tool": "test_tool", "result": "test_result"}]
    response = swarm.process_message("test_agent", message, tool_results=tool_results)
    assert response == "Test response"
    mock_agent.process_message.assert_called_once_with(
        message, tool_results=tool_results
    )


def test_format_context() -> None:
    """Test context formatting."""
    swarm = Swarm({})
    prev_responses = ["Response 1", "Response 2"]
    context = swarm._format_context(prev_responses)

    assert "Previous responses:" in context
    assert "Response 1" in context
    assert "Response 2" in context
    assert "What are your thoughts on the discussion so far?" in context


def test_process_round(swarm: Swarm, mock_agent2: BedrockAgent) -> None:
    """Test processing a single discussion round."""
    swarm.add_agent(mock_agent2, "test_agent2")
    prev_responses = ["Previous response"]

    responses = swarm._process_round(prev_responses)

    assert len(responses) == 2
    assert "test_agent" in responses
    assert "test_agent2" in responses
    assert responses["test_agent"]["content"] == "Test response"
    assert responses["test_agent2"]["content"] == "Test response 2"


def test_discuss(swarm: Swarm, mock_agent2: BedrockAgent) -> None:
    """Test multi-round discussion."""
    swarm.add_agent(mock_agent2, "test_agent2")
    topic = "Test topic"

    history = swarm.discuss(topic, rounds=3)

    # Check history length (3 rounds)
    assert len(history) == 3

    # Check first round (initial topic)
    assert len(history[0]) == 2  # Two agents
    assert "test_agent" in history[0]
    assert "test_agent2" in history[0]

    # Check subsequent rounds
    for round_responses in history[1:]:
        assert len(round_responses) == 2
        assert "test_agent" in round_responses
        assert "test_agent2" in round_responses


def test_broadcast(swarm: Swarm, mock_agent2: BedrockAgent) -> None:
    """Test message broadcasting."""
    swarm.add_agent(mock_agent2, "test_agent2")
    message = "Broadcast message"

    # Test broadcasting to all agents
    responses = swarm.broadcast(message)
    assert len(responses) == 2
    assert any(r["agent_id"] == "test_agent" for r in responses)
    assert any(r["agent_id"] == "test_agent2" for r in responses)

    # Test broadcasting with exclusion
    responses = swarm.broadcast(message, exclude=["test_agent2"])
    assert len(responses) == 1
    assert responses[0]["agent_id"] == "test_agent"


def test_discuss_single_round(swarm: Swarm) -> None:
    """Test discussion with a single round."""
    topic = "Test topic"
    history = swarm.discuss(topic, rounds=1)

    assert len(history) == 1
    assert "test_agent" in history[0]
    assert history[0]["test_agent"]["content"] == "Test response"
