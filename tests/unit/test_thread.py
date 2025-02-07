"""Tests for thread implementation."""

from datetime import datetime
from typing import Optional, TypedDict
from unittest.mock import MagicMock, patch

import pytest

from bedrock_swarm.agency.thread import Thread
from bedrock_swarm.agents.base import BedrockAgent
from bedrock_swarm.config import AWSConfig
from bedrock_swarm.memory.base import Message
from bedrock_swarm.tools.base import BaseTool


class ToolCallResult(TypedDict):
    """Type definition for tool call results."""

    tool_call_id: str
    output: str
    error: Optional[str]


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
def aws_config() -> AWSConfig:
    """Create AWS config for testing."""
    return AWSConfig(region="us-west-2", profile="default")


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
            tools=[MockTool()],
        )


@pytest.fixture
def thread(agent: BedrockAgent) -> Thread:
    """Create a test thread."""
    thread = Thread(agent)
    thread.event_system = MagicMock()
    thread.event_system.create_event = MagicMock(return_value="event_id")
    return thread


def test_thread_initialization(thread: Thread) -> None:
    """Test thread initialization."""
    assert thread.agent is not None
    assert len(thread.history) == 0
    assert thread.current_run is None
    assert len(thread.runs) == 0


def test_process_message_basic(thread: Thread) -> None:
    """Test basic message processing."""
    with patch.object(thread.agent, "generate") as mock_generate:
        mock_generate.return_value = {"type": "message", "content": "Test response"}
        response = thread.process_message("Test message")
        assert response == "Test response"
        assert len(thread.runs) == 1
        assert thread.runs[0].status == "completed"


def test_process_message_with_tool_results(thread: Thread) -> None:
    """Test processing a message with tool results."""
    assert thread.agent is not None

    # Mock tool call response
    tool_call_response = {
        "type": "tool_call",
        "tool_calls": [
            {
                "id": "call_1",
                "type": "function",
                "function": {
                    "name": "mock_tool",
                    "arguments": '{"param": "test"}',
                },
            }
        ],
    }

    # Mock final response
    final_response = {"content": "Test response"}

    with patch.object(thread.agent, "generate") as mock_generate:
        mock_generate.side_effect = [tool_call_response, final_response]
        response = thread.process_message("Test message")
        assert response == "Test response"
        assert len(thread.runs) == 1
        assert thread.runs[0].status == "completed"


def test_add_message(thread: Thread) -> None:
    """Test adding a message."""
    message = Message(
        role="human",
        content="Test message",
        timestamp=datetime.now(),
    )
    thread.history.append(message)
    assert len(thread.history) == 1
    assert thread.history[0] == message


def test_get_messages(thread: Thread) -> None:
    """Test getting messages."""
    message1 = Message(
        role="human",
        content="Message 1",
        timestamp=datetime.now(),
    )
    message2 = Message(
        role="assistant",
        content="Message 2",
        timestamp=datetime.now(),
    )
    thread.history.extend([message1, message2])
    messages = thread.get_history()
    assert len(messages) == 2
    assert messages[0] == message1
    assert messages[1] == message2


def test_thread_init(thread: Thread) -> None:
    """Test Thread initialization."""
    # Create a new thread without event system for this test
    test_thread = Thread(thread.agent)
    assert isinstance(test_thread.id, str)
    assert isinstance(test_thread.history, list)
    assert isinstance(test_thread.runs, list)
    assert test_thread.current_run is None
    assert test_thread.event_system is None


def test_thread_get_history(thread: Thread) -> None:
    """Test getting thread history."""
    # Add messages
    thread.history.append(
        Message(
            role="user",
            content="Test message",
            timestamp=datetime.now(),
        )
    )
    thread.history.append(
        Message(
            role="assistant",
            content="Test response",
            timestamp=datetime.now(),
        )
    )

    # Check history
    history = thread.history
    assert len(history) == 2
    assert history[0].role == "user"
    assert history[0].content == "Test message"
    assert history[1].role == "assistant"
    assert history[1].content == "Test response"
