"""Tests for the thread module."""

from datetime import datetime
from typing import Any, Dict, List, Optional, TypedDict, cast
from unittest.mock import MagicMock, patch

import pytest

from bedrock_swarm.agency.thread import Thread, ThreadMessage
from bedrock_swarm.agents.base import BedrockAgent
from bedrock_swarm.config import AWSConfig
from bedrock_swarm.tools.base import BaseTool


class ToolCallResult(TypedDict):
    """Type definition for tool call results."""

    tool_call_id: str
    output: str
    error: Optional[str]


class MockTool(BaseTool):
    """Mock tool for testing."""

    def __init__(
        self, name: str = "mock_tool", description: str = "Mock tool for testing"
    ) -> None:
        """Initialize mock tool."""
        self._name = name
        self._description = description
        self._execute_mock = MagicMock(return_value="Tool result")

    @property
    def name(self) -> str:
        """Get tool name."""
        return self._name

    @property
    def description(self) -> str:
        """Get tool description."""
        return self._description

    def get_schema(self) -> Dict[str, Any]:
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

    def _execute_impl(self, **kwargs: Any) -> str:
        """Execute the mock tool."""
        return cast(str, self._execute_mock(**kwargs))


@pytest.fixture
def aws_config() -> AWSConfig:
    """Create AWS config for testing."""
    return AWSConfig(region="us-west-2", profile="default")


@pytest.fixture
def agent(aws_config: AWSConfig) -> BedrockAgent:
    """Create agent for testing."""
    agent = BedrockAgent(
        name="test_agent",
        model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        aws_config=aws_config,
    )
    # Mock the process_message method
    mock_process = MagicMock(return_value="Test response")
    with patch.object(agent, "process_message", mock_process):
        return agent


@pytest.fixture
def thread(agent: BedrockAgent) -> Thread:
    """Create thread for testing."""
    return Thread(agent=agent)


def test_thread_initialization(thread: Thread) -> None:
    """Test thread initialization."""
    assert thread.agent is not None
    assert thread.history == []


def test_add_message(thread: Thread) -> None:
    """Test adding a message."""
    thread.execute("Test message")
    assert len(thread.history) == 2  # Human message + assistant response
    assert thread.history[0].content == "Test message"
    assert thread.history[0].role == "human"


def test_add_message_with_tool_results(thread: Thread) -> None:
    """Test adding a message with tool results."""
    tool_results: List[ToolCallResult] = [
        {
            "tool_call_id": "test_id",
            "output": "test_result",
            "error": None,
        }
    ]
    thread.execute("Test message", tool_results=tool_results)
    assert len(thread.history) == 2  # Human message + assistant response
    assert thread.history[0].content == "Test message"
    assert thread.history[0].role == "human"
    assert thread.history[0].tool_call_results == tool_results


def test_get_messages(thread: Thread) -> None:
    """Test getting messages."""
    thread.execute("Message 1")
    thread.execute("Message 2")
    messages = thread.get_history()
    assert len(messages) == 4  # 2 human messages + 2 assistant responses
    assert messages[0].content == "Message 1"
    assert messages[2].content == "Message 2"


def test_clear_messages(thread: Thread) -> None:
    """Test clearing messages."""
    thread.execute("Test message")
    thread.clear_history()
    assert len(thread.history) == 0


def test_process_message(thread: Thread) -> None:
    """Test processing a message."""
    assert thread.agent is not None
    mock_process = MagicMock(return_value="Test response")
    with patch.object(thread.agent, "process_message", mock_process):
        response = thread.execute("Test message")
        assert response.content == "Test response"
        assert len(thread.history) == 2
        assert thread.history[0].content == "Test message"
        assert thread.history[1].content == "Test response"
        mock_process.assert_called_once_with("Test message", None)


def test_process_message_with_tool_results(thread: Thread) -> None:
    """Test processing a message with tool results."""
    assert thread.agent is not None
    mock_process = MagicMock(return_value="Test response with tool result")
    with patch.object(thread.agent, "process_message", mock_process):
        tool_results: List[ToolCallResult] = [
            {
                "tool_call_id": "test_id",
                "output": "test_result",
                "error": None,
            }
        ]
        response = thread.execute("Test message", tool_results=tool_results)
        assert response.content == "Test response with tool result"
        assert len(thread.history) == 2
        assert thread.history[0].content == "Test message"
        assert thread.history[0].tool_call_results == tool_results
        assert thread.history[1].content == "Test response with tool result"


def test_message_init() -> None:
    """Test ThreadMessage initialization."""
    timestamp = datetime.now()
    message = ThreadMessage(
        content="Test message",
        role="human",
        timestamp=timestamp,
        tool_calls=[{"name": "test_tool"}],
        tool_call_results=[
            {
                "tool_call_id": "test_id",
                "output": "result",
                "error": None,
            }
        ],
        metadata={"key": "value"},
    )

    assert message.content == "Test message"
    assert message.role == "human"
    assert message.timestamp == timestamp
    assert message.tool_calls == [{"name": "test_tool"}]
    assert message.tool_call_results == [
        {
            "tool_call_id": "test_id",
            "output": "result",
            "error": None,
        }
    ]
    assert message.metadata == {"key": "value"}


def test_thread_init(thread: Thread) -> None:
    """Test Thread initialization."""
    assert isinstance(thread.thread_id, str)
    assert isinstance(thread.history, list)
    assert isinstance(thread.active_tools, dict)


def test_thread_execute_simple(thread: Thread) -> None:
    """Test executing a simple message in thread."""
    assert thread.agent is not None
    mock_process = MagicMock(return_value="Test response")
    with patch.object(thread.agent, "process_message", mock_process):
        message = "Test message"
        response = thread.execute(message)

        assert isinstance(response, ThreadMessage)
        assert response.content == "Test response"
        assert len(thread.history) == 2  # Human message + assistant response
        assert thread.history[0].role == "human"
        assert thread.history[0].content == "Test message"
        assert thread.history[1].role == "assistant"
        assert thread.history[1].content == "Test response"


def test_thread_execute_with_tools(thread: Thread) -> None:
    """Test executing a message with tools."""
    assert thread.agent is not None
    # Add a mock tool
    tool = MockTool(name="mock_tool")
    thread.agent.add_tool(tool)

    # Set up mock response with tool call
    mock_process = MagicMock(return_value="Test response with tool result")
    with patch.object(thread.agent, "process_message", new=mock_process):
        response = thread.execute("Test message")

        assert isinstance(response, ThreadMessage)
        assert response.content == "Test response with tool result"
        assert len(thread.history) == 2  # Human message + assistant response
        assert thread.history[0].role == "human"
        assert thread.history[0].content == "Test message"
        assert thread.history[1].role == "assistant"
        assert thread.history[1].content == "Test response with tool result"

        # Verify process_message was called with the tool
        mock_process.assert_called_once_with("Test message", None)


def test_thread_get_history(thread: Thread) -> None:
    """Test getting thread history."""
    # Add some messages
    messages = [
        ThreadMessage(role="human", content="Message 1", timestamp=datetime.now()),
        ThreadMessage(
            role="assistant",
            content="Response 1",
            timestamp=datetime.now(),
            tool_calls=[{"name": "test_tool"}],
            tool_call_results=[
                {
                    "tool_call_id": "test_id",
                    "output": "result",
                    "error": None,
                }
            ],
        ),
        ThreadMessage(role="human", content="Message 2", timestamp=datetime.now()),
    ]
    thread.history.extend(messages)

    # Get full history
    history = thread.get_formatted_history()
    assert len(history) == 3
    assert history[0]["content"] == "Message 1"
    assert history[1]["tool_calls"] == [{"name": "test_tool"}]
    assert history[1]["tool_call_results"] == [
        {
            "tool_call_id": "test_id",
            "output": "result",
            "error": None,
        }
    ]

    # Get limited history
    limited = thread.get_formatted_history(limit=2)
    assert len(limited) == 2
    assert limited[0]["content"] == "Response 1"

    # Get history without tools
    no_tools = thread.get_formatted_history(include_tools=False)
    assert "tool_calls" not in no_tools[1]
    assert "tool_call_results" not in no_tools[1]


def test_thread_clear_history(thread: Thread) -> None:
    """Test clearing thread history."""
    # Add some messages
    messages = [
        ThreadMessage(role="human", content="Message 1", timestamp=datetime.now()),
        ThreadMessage(role="assistant", content="Response 1", timestamp=datetime.now()),
    ]
    thread.history.extend(messages)

    thread.clear_history()
    assert len(thread.history) == 0
