"""Tests for thread implementation."""

from datetime import datetime
from typing import Optional, TypedDict
from unittest.mock import MagicMock, patch

import pytest

from bedrock_swarm.agency.thread import Run, Thread
from bedrock_swarm.agents.base import BedrockAgent
from bedrock_swarm.memory.base import Message
from bedrock_swarm.tools.base import BaseTool


class ToolCallResult(TypedDict):
    """Type definition for tool call results."""

    tool_call_id: str
    output: str
    error: Optional[str]


class MockTool(BaseTool):
    """Mock tool for testing."""

    def __init__(self, should_fail: bool = False) -> None:
        """Initialize mock tool."""
        self._name = "mock_tool"
        self._description = "Mock tool for testing"
        self.should_fail = should_fail

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
        if self.should_fail:
            raise ValueError("Tool execution failed")
        return f"Mock result: {kwargs['param']}"


@pytest.fixture(autouse=True)
def mock_aws_config():
    """Mock AWS configuration."""
    mock_config = MagicMock()
    mock_config.region = "us-west-2"
    mock_config.profile = "default"
    mock_config.endpoint_url = "https://bedrock-runtime.us-west-2.amazonaws.com"

    with patch("bedrock_swarm.agents.base.AWSConfig") as mock_config_class:
        mock_config_class.region = "us-west-2"
        mock_config_class.profile = "default"
        mock_config_class.endpoint_url = (
            "https://bedrock-runtime.us-west-2.amazonaws.com"
        )
        mock_config_class.return_value = mock_config
        yield mock_config_class


@pytest.fixture
def mock_model() -> MagicMock:
    """Create a mock model."""
    mock = MagicMock()
    mock.invoke.return_value = {"type": "message", "content": "Test response"}
    return mock


@pytest.fixture
def agent(mock_model: MagicMock) -> BedrockAgent:
    """Create a test agent."""
    with patch("bedrock_swarm.models.factory.ModelFactory.create_model") as mock_create:
        mock_create.return_value = mock_model
        return BedrockAgent(
            name="test",
            model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
            role="Test agent",
            tools=[MockTool()],
        )


@pytest.fixture
def thread(agent: BedrockAgent) -> Thread:
    """Create a test thread."""
    thread = Thread(agent)
    thread.event_system = MagicMock()
    thread.event_system.create_event = MagicMock(return_value="event_id")
    return thread


def test_run_lifecycle() -> None:
    """Test run state transitions."""
    run = Run()
    assert run.status == "queued"
    assert run.started_at is not None
    assert run.completed_at is None
    assert run.last_error is None
    assert len(run.tool_calls) == 0

    # Test completion
    run.complete()
    assert run.status == "completed"
    assert run.completed_at is not None

    # Test failure
    run = Run()
    run.fail("Test error")
    assert run.status == "failed"
    assert run.last_error == "Test error"
    assert run.completed_at is not None

    # Test requiring action
    run = Run()
    tool_calls = [
        {
            "id": "test",
            "type": "function",
            "function": {"name": "test", "arguments": {}},
        }
    ]
    run.require_action({"type": "tool_calls", "tool_calls": tool_calls})
    assert run.status == "requires_action"
    assert run.required_action == {"type": "tool_calls", "tool_calls": tool_calls}
    assert run.tool_calls == tool_calls


def test_thread_initialization(thread: Thread) -> None:
    """Test thread initialization."""
    assert thread.agent is not None
    assert len(thread.history) == 0
    assert thread.current_run is None
    assert len(thread.runs) == 0
    assert isinstance(thread.id, str)
    assert thread.created_at is not None
    assert thread.last_message_at is None


def test_process_message_basic(thread: Thread) -> None:
    """Test basic message processing."""
    with patch.object(thread.agent, "generate") as mock_generate:
        mock_generate.return_value = {"type": "message", "content": "Test response"}
        response = thread.process_message("Test message")

        # Verify response
        assert response == "Test response"

        # Verify run state
        assert len(thread.runs) == 1
        assert thread.runs[0].status == "completed"
        assert thread.runs[0].completed_at is not None

        # Verify events
        thread.event_system.create_event.assert_any_call(
            type="agent_start",
            agent_name=thread.agent.name,
            run_id=thread.runs[0].id,
            thread_id=thread.id,
            details={"message": "Test message"},
        )
        thread.event_system.create_event.assert_any_call(
            type="agent_complete",
            agent_name=thread.agent.name,
            run_id=thread.runs[0].id,
            thread_id=thread.id,
            details={"response": "Test response"},
        )


def test_process_message_with_tool_calls(thread: Thread) -> None:
    """Test processing a message with tool calls."""
    # Mock tool call response
    tool_call_response = {
        "type": "tool_call",
        "tool_calls": [
            {
                "id": "call_1",
                "type": "function",
                "function": {
                    "name": "mock_tool",
                    "arguments": {"param": "test"},
                },
            }
        ],
    }

    # Mock final response
    final_response = {"type": "message", "content": "Final response"}

    with patch.object(thread.agent, "generate") as mock_generate:
        mock_generate.side_effect = [tool_call_response, final_response]
        response = thread.process_message("Test message")

        # Verify response
        assert response == "Final response"

        # Verify run state
        assert len(thread.runs) == 1
        run = thread.runs[0]
        assert run.status == "completed"
        assert len(run.tool_calls) == 1
        assert run.tool_calls[0]["id"] == "call_1"

        # Verify events
        thread.event_system.create_event.assert_any_call(
            type="tool_start",
            agent_name=thread.agent.name,
            run_id=run.id,
            thread_id=thread.id,
            details={
                "tool_name": "mock_tool",
                "arguments": {"param": "test"},
            },
        )
        thread.event_system.create_event.assert_any_call(
            type="tool_complete",
            agent_name=thread.agent.name,
            run_id=run.id,
            thread_id=thread.id,
            details={
                "tool_name": "mock_tool",
                "arguments": {"param": "test"},
                "result": "Mock result: test",
            },
        )


def test_process_message_with_tool_error(thread: Thread) -> None:
    """Test processing a message with tool execution error."""
    # Add failing tool
    thread.agent.tools["failing_tool"] = MockTool(should_fail=True)

    # Mock tool call response
    tool_call_response = {
        "type": "tool_call",
        "tool_calls": [
            {
                "id": "call_1",
                "type": "function",
                "function": {
                    "name": "failing_tool",
                    "arguments": {"param": "test"},
                },
            }
        ],
    }

    with patch.object(thread.agent, "generate") as mock_generate:
        mock_generate.return_value = tool_call_response
        response = thread.process_message("Test message")

        # Verify error response
        assert "I encountered an error while processing your request" in response
        assert "Tool execution failed" in response

        # Verify run state
        assert len(thread.runs) == 1
        run = thread.runs[0]
        assert run.status == "completed"  # Tool errors don't fail the run

        # Verify events
        thread.event_system.create_event.assert_any_call(
            type="tool_start",
            agent_name=thread.agent.name,
            run_id=run.id,
            thread_id=thread.id,
            details={
                "tool_name": "failing_tool",
                "arguments": {"param": "test"},
            },
        )
        thread.event_system.create_event.assert_any_call(
            type="agent_complete",
            agent_name=thread.agent.name,
            run_id=run.id,
            thread_id=thread.id,
            details={
                "response": "I encountered an error while processing your request: Tool execution failed"
            },
        )


def test_process_message_with_invalid_tool(thread: Thread) -> None:
    """Test processing a message with invalid tool name."""
    # Mock tool call response with non-existent tool
    tool_call_response = {
        "type": "tool_call",
        "tool_calls": [
            {
                "id": "call_1",
                "type": "function",
                "function": {
                    "name": "non_existent_tool",
                    "arguments": {"param": "test"},
                },
            }
        ],
    }

    with patch.object(thread.agent, "generate") as mock_generate:
        mock_generate.return_value = tool_call_response
        response = thread.process_message("Test message")

        # Verify error response
        assert "I encountered an error while processing your request" in response
        assert "Tool non_existent_tool not found" in response

        # Verify run state
        assert len(thread.runs) == 1
        run = thread.runs[0]
        assert run.status == "completed"  # Tool errors don't fail the run


def test_process_message_with_invalid_arguments(thread: Thread) -> None:
    """Test processing a message with invalid tool arguments."""
    # Mock tool call response with invalid JSON arguments
    tool_call_response = {
        "type": "tool_call",
        "tool_calls": [
            {
                "id": "call_1",
                "type": "function",
                "function": {
                    "name": "mock_tool",
                    "arguments": "invalid json",
                },
            }
        ],
    }

    with patch.object(thread.agent, "generate") as mock_generate:
        mock_generate.return_value = tool_call_response
        response = thread.process_message("Test message")

        # Verify error response
        assert "I encountered an error while processing your request" in response
        assert "Invalid tool arguments JSON" in response

        # Verify run state
        assert len(thread.runs) == 1
        run = thread.runs[0]
        assert run.status == "completed"  # Tool errors don't fail the run


def test_process_message_with_agent_error(thread: Thread) -> None:
    """Test processing a message when agent.generate raises an error."""
    with patch.object(thread.agent, "generate") as mock_generate:
        mock_generate.side_effect = Exception("Agent error")
        response = thread.process_message("Test message")

        # Verify error response
        assert (
            "Error processing message" in response
        )  # Different error format for agent errors
        assert "Agent error" in response

        # Verify run state
        assert len(thread.runs) == 1
        run = thread.runs[0]
        assert run.status == "failed"  # Agent errors do fail the run
        assert "Agent error" in run.last_error

        # Verify events
        thread.event_system.create_event.assert_any_call(
            type="error",
            agent_name=thread.agent.name,
            run_id=run.id,
            thread_id=thread.id,
            details={"error": run.last_error},
        )


def test_get_history(thread: Thread) -> None:
    """Test getting thread history."""
    # Add messages
    messages = [
        Message(role="user", content="Message 1", timestamp=datetime.now()),
        Message(role="assistant", content="Response 1", timestamp=datetime.now()),
        Message(role="user", content="Message 2", timestamp=datetime.now()),
    ]
    thread.history.extend(messages)

    # Get full history
    history = thread.get_history()
    assert len(history) == 3
    assert all(isinstance(msg, Message) for msg in history)
    assert [msg.content for msg in history] == ["Message 1", "Response 1", "Message 2"]

    # Get context window
    context = thread.get_context_window(n=2)
    assert len(context) == 2
    assert [msg.content for msg in context] == ["Response 1", "Message 2"]


def test_run_management(thread: Thread) -> None:
    """Test run management functions."""
    # Create some runs
    run1 = Run()
    run2 = Run()
    thread.runs.extend([run1, run2])
    thread.current_run = run2

    # Test get_run
    assert thread.get_run(run1.id) == run1
    assert thread.get_run(run2.id) == run2
    assert thread.get_run("non_existent") is None

    # Test get_current_run
    assert thread.get_current_run() == run2

    # Test cancel_run
    assert thread.cancel_run(run1.id) is True
    assert run1.status == "failed"
    assert "Run cancelled by user" in run1.last_error

    # Test cancelling already completed run
    run2.complete()
    assert thread.cancel_run(run2.id) is False
    assert run2.status == "completed"
