"""Tests for agent implementation."""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from bedrock_swarm.agents.base import BedrockAgent
from bedrock_swarm.exceptions import InvalidModelError
from bedrock_swarm.memory.base import Message, SimpleMemory
from bedrock_swarm.tools.base import BaseTool


class MockTool(BaseTool):
    """Mock tool for testing."""

    def __init__(self) -> None:
        """Initialize mock tool."""
        self._name = "mock_tool"
        self._description = "Mock tool for testing"

    @property
    def name(self) -> str:
        """Get tool name."""
        return self._name

    @property
    def description(self) -> str:
        """Get tool description."""
        return self._description

    def get_schema(self) -> dict:
        """Get tool schema."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "param": {"type": "string"},
                },
                "required": ["param"],
            },
        }

    def _execute_impl(self, **kwargs) -> str:
        """Execute the tool."""
        return f"Mock result: {kwargs['param']}"


@pytest.fixture
def mock_model() -> MagicMock:
    """Create a mock model."""
    mock = MagicMock()
    mock.invoke.return_value = {"content": "Test response"}
    return mock


@pytest.fixture
def agent(mock_model: MagicMock) -> BedrockAgent:
    """Create a test agent."""
    with patch("bedrock_swarm.models.factory.ModelFactory.create_model") as mock_create:
        mock_create.return_value = mock_model
        return BedrockAgent(
            name="test",
            model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        )


def test_agent_initialization(agent: BedrockAgent) -> None:
    """Test agent initialization."""
    assert agent.name == "test"
    assert agent.model_id == "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
    assert len(agent.tools) == 0
    assert isinstance(agent.memory, SimpleMemory)


def test_agent_validate_model_id() -> None:
    """Test model ID validation."""
    # Valid model ID
    agent = BedrockAgent(
        name="test",
        model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    )
    assert agent.model_id == "us.anthropic.claude-3-5-sonnet-20241022-v2:0"

    # Invalid model ID should raise InvalidModelError
    with pytest.raises(InvalidModelError, match="Unsupported model family"):
        BedrockAgent(
            name="test",
            model_id="test.model",
        )


def test_agent_generate(agent: BedrockAgent, mock_model: MagicMock) -> None:
    """Test message generation."""
    # Test basic generation
    response = agent.generate("Test message")
    assert response["content"] == "Test response"

    # Verify model was called correctly
    mock_model.invoke.assert_called_once()
    args = mock_model.invoke.call_args[1]
    assert "Test message" in args["message"]


def test_agent_memory(agent: BedrockAgent) -> None:
    """Test memory management."""
    # Add messages
    agent.memory.add_message(
        Message(
            role="user",
            content="Test message",
            timestamp=datetime.now(),
        )
    )
    agent.memory.add_message(
        Message(
            role="assistant",
            content="Test response",
            timestamp=datetime.now(),
        )
    )

    # Check messages
    messages = agent.memory.get_messages()
    assert len(messages) == 2
    assert messages[0].role == "user"
    assert messages[0].content == "Test message"
    assert messages[1].role == "assistant"
    assert messages[1].content == "Test response"
