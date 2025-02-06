"""Tests for the thread module."""

from datetime import datetime
from unittest.mock import MagicMock

import pytest

from bedrock_swarm.agency.thread import Thread, ThreadMessage
from bedrock_swarm.agents.base import BedrockAgent
from bedrock_swarm.config import AWSConfig
from bedrock_swarm.tools.base import BaseTool


class MockTool(BaseTool):
    """Mock tool for testing."""

    def __init__(
        self, name: str = "mock_tool", description: str = "Mock tool for testing"
    ):
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

    def _execute_impl(self, **kwargs):
        """Execute the mock tool."""
        return self._execute_mock(**kwargs)


@pytest.fixture
def aws_config():
    """Create AWS config for testing."""
    return AWSConfig(region="us-west-2", profile="default")


@pytest.fixture
def agent(aws_config):
    """Create agent for testing."""
    return BedrockAgent(
        name="test_agent",
        model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        aws_config=aws_config,
    )


@pytest.fixture
def thread(agent):
    """Create thread for testing."""
    return Thread(agent=agent)


def test_thread_initialization(thread):
    """Test thread initialization."""
    assert thread.agent is not None
    assert thread.history == []


def test_add_message(thread):
    """Test adding a message."""
    thread.execute("Test message")
    assert len(thread.history) == 2  # Human message + assistant response
    assert thread.history[0].content == "Test message"
    assert thread.history[0].role == "human"


def test_add_message_with_tool_results(thread):
    """Test adding a message with tool results."""
    tool_results = [{"tool": "test_tool", "result": "test_result"}]
    thread.execute("Test message", tool_results=tool_results)
    assert len(thread.history) == 2  # Human message + assistant response
    assert thread.history[0].content == "Test message"
    assert thread.history[0].role == "human"
    assert thread.history[0].tool_call_results == tool_results


def test_get_messages(thread):
    """Test getting messages."""
    thread.execute("Message 1")
    thread.execute("Message 2")
    messages = thread.get_history()
    assert len(messages) == 4  # 2 human messages + 2 assistant responses
    assert messages[0].content == "Message 1"
    assert messages[2].content == "Message 2"


def test_clear_messages(thread):
    """Test clearing messages."""
    thread.execute("Test message")
    thread.clear_history()
    assert len(thread.history) == 0


def test_process_message(thread):
    """Test processing a message."""
    thread.agent.process_message = MagicMock(return_value="Test response")
    response = thread.execute("Test message")
    assert response.content == "Test response"
    assert len(thread.history) == 2
    assert thread.history[0].content == "Test message"
    assert thread.history[1].content == "Test response"


def test_process_message_with_tool_results(thread):
    """Test processing a message with tool results."""
    thread.agent.process_message = MagicMock(
        return_value="Test response with tool result"
    )
    tool_results = [{"tool": "test_tool", "result": "test_result"}]
    response = thread.execute("Test message", tool_results=tool_results)
    assert response.content == "Test response with tool result"
    assert len(thread.history) == 2
    assert thread.history[0].content == "Test message"
    assert thread.history[0].tool_call_results == tool_results
    assert thread.history[1].content == "Test response with tool result"


def test_message_init():
    """Test ThreadMessage initialization."""
    timestamp = datetime.now()
    message = ThreadMessage(
        content="Test message",
        role="human",
        timestamp=timestamp,
        tool_calls=[{"name": "test_tool"}],
        tool_call_results=[{"name": "test_tool", "result": "result"}],
        metadata={"key": "value"},
    )

    assert message.content == "Test message"
    assert message.role == "human"
    assert message.timestamp == timestamp
    assert message.tool_calls == [{"name": "test_tool"}]
    assert message.tool_call_results == [{"name": "test_tool", "result": "result"}]
    assert message.metadata == {"key": "value"}


def test_thread_init(thread):
    """Test Thread initialization."""
    assert isinstance(thread.thread_id, str)
    assert isinstance(thread.history, list)
    assert isinstance(thread.active_tools, dict)


def test_thread_execute_simple(thread):
    """Test executing a simple message in thread."""
    thread.agent.process_message = MagicMock(return_value="Test response")

    message = "Test message"
    response = thread.execute(message)

    assert isinstance(response, ThreadMessage)
    assert response.content == "Test response"
    assert len(thread.history) == 2  # Human message + assistant response
    assert thread.history[0].role == "human"
    assert thread.history[0].content == "Test message"
    assert thread.history[1].role == "assistant"
    assert thread.history[1].content == "Test response"


def test_thread_execute_with_tools(thread):
    """Test executing a message with tools."""
    # Add a mock tool
    tool = MockTool(name="mock_tool")
    thread.agent.add_tool(tool)

    # Set up mock response with tool call
    thread.agent.process_message = MagicMock(
        return_value="Test response with tool result"
    )

    response = thread.execute("Test message")

    assert isinstance(response, ThreadMessage)
    assert "Test response with tool result" in response.content
    assert len(thread.history) == 2  # Human message + assistant response


def test_thread_get_history(thread):
    """Test getting thread history."""
    # Add some messages
    messages = [
        ThreadMessage(role="human", content="Message 1", timestamp=datetime.now()),
        ThreadMessage(
            role="assistant",
            content="Response 1",
            timestamp=datetime.now(),
            tool_calls=[{"name": "test_tool"}],
            tool_call_results=[{"name": "test_tool", "result": "result"}],
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
        {"name": "test_tool", "result": "result"}
    ]

    # Get limited history
    limited = thread.get_formatted_history(limit=2)
    assert len(limited) == 2
    assert limited[0]["content"] == "Response 1"

    # Get history without tools
    no_tools = thread.get_formatted_history(include_tools=False)
    assert "tool_calls" not in no_tools[1]
    assert "tool_call_results" not in no_tools[1]


def test_thread_clear_history(thread):
    """Test clearing thread history."""
    # Add some messages
    messages = [
        ThreadMessage(role="human", content="Message 1", timestamp=datetime.now()),
        ThreadMessage(role="assistant", content="Response 1", timestamp=datetime.now()),
    ]
    thread.history.extend(messages)

    thread.clear_history()
    assert len(thread.history) == 0
