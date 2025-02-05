"""Tests for the agency module."""

from unittest.mock import Mock, patch

import pytest

from bedrock_swarm.agency.agency import Agency
from bedrock_swarm.agents.base import BedrockAgent
from bedrock_swarm.config import AWSConfig
from bedrock_swarm.tools.base import BaseTool


class MockTool(BaseTool):
    """Mock tool for testing."""

    def __init__(self, name="mock_tool"):
        """Initialize mock tool."""
        super().__init__(name=name)
        self._execute_mock = Mock(return_value="Tool result")

    def execute(self, **kwargs):
        """Execute the tool."""
        return self._execute_mock(**kwargs)

    def get_schema(self):
        """Get tool schema."""
        return {
            "name": self.name,
            "description": "Mock tool for testing",
            "parameters": {
                "type": "object",
                "properties": {
                    "param1": {"type": "string"},
                    "param2": {"type": "integer"},
                },
                "required": ["param1"],
            },
        }


@pytest.fixture
def aws_config():
    """Create AWS config for testing."""
    return AWSConfig(region="us-west-2", profile="default")


@pytest.fixture
def agency(aws_config):
    """Create agency for testing."""
    return Agency(aws_config=aws_config)


def test_agency_initialization(agency):
    """Test agency initialization."""
    assert agency.aws_config is not None
    assert agency.agents == {}


def test_create_agent(agency):
    """Test creating an agent."""
    agent = agency.create_agent(
        name="test_agent",
        model_id="anthropic.claude-v2",
        instructions="Test instructions",
    )
    assert agent.name == "test_agent"
    assert agent.model_id == "anthropic.claude-v2"
    assert agent.instructions == "Test instructions"
    assert "test_agent" in agency.agents


def test_get_agent(agency):
    """Test getting an agent."""
    agent = agency.create_agent(
        name="test_agent",
        model_id="anthropic.claude-v2",
    )
    retrieved_agent = agency.get_agent("test_agent")
    assert retrieved_agent == agent


def test_get_nonexistent_agent(agency):
    """Test getting a nonexistent agent."""
    with pytest.raises(KeyError):
        agency.get_agent("nonexistent_agent")


def test_remove_agent(agency):
    """Test removing an agent."""
    agency.create_agent(
        name="test_agent",
        model_id="anthropic.claude-v2",
    )
    agency.remove_agent("test_agent")
    assert "test_agent" not in agency.agents


def test_remove_nonexistent_agent(agency):
    """Test removing a nonexistent agent."""
    with pytest.raises(KeyError):
        agency.remove_agent("nonexistent_agent")


def test_clear_agents(agency):
    """Test clearing all agents."""
    agency.create_agent(
        name="agent1",
        model_id="anthropic.claude-v2",
    )
    agency.create_agent(
        name="agent2",
        model_id="anthropic.claude-v2",
    )
    agency.clear_agents()
    assert len(agency.agents) == 0


def test_process_message(agency):
    """Test processing a message."""
    agent = agency.create_agent(
        name="test_agent",
        model_id="anthropic.claude-v2",
    )
    agent.process_message = Mock(return_value="Test result")
    response = agency.process_message("test_agent", "Test message")
    assert response == "Test result"
    agent.process_message.assert_called_once_with("Test message", None)


def test_process_message_with_nonexistent_agent(agency):
    """Test processing a message with a nonexistent agent."""
    with pytest.raises(KeyError):
        agency.process_message("nonexistent_agent", "Test message")
