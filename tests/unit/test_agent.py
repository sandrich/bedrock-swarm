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
            role="Test agent for unit testing",
        )


def test_agent_initialization(agent: BedrockAgent) -> None:
    """Test agent initialization."""
    assert agent.name == "test"
    assert agent.model_id == "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
    assert agent.role == "Test agent for unit testing"
    assert len(agent.tools) == 0
    assert isinstance(agent.memory, SimpleMemory)
    assert agent.system_prompt is None

    # Test initialization with all optional parameters
    tool = MockTool()
    memory = SimpleMemory()
    agent_with_opts = BedrockAgent(
        name="test_full",
        model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        role="Full test agent",
        tools=[tool],
        memory=memory,
        system_prompt="Test system prompt",
    )
    assert agent_with_opts.name == "test_full"
    assert len(agent_with_opts.tools) == 1
    assert agent_with_opts.tools[tool.name] == tool
    assert agent_with_opts.memory == memory
    assert agent_with_opts.system_prompt == "Test system prompt"


def test_agent_validate_model_id() -> None:
    """Test model ID validation."""
    # Valid model ID
    agent = BedrockAgent(
        name="test",
        model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        role="Test agent for validation",
    )
    assert agent.model_id == "us.anthropic.claude-3-5-sonnet-20241022-v2:0"

    # Invalid model ID should raise InvalidModelError
    with pytest.raises(InvalidModelError, match="Unsupported model family"):
        BedrockAgent(
            name="test",
            model_id="test.model",
            role="Test agent for validation",
        )


def test_build_prompt(agent: BedrockAgent) -> None:
    """Test prompt building."""
    # Test basic prompt
    prompt = agent._build_prompt("Test message")
    assert (
        "You are a specialized agent with expertise in: Test agent for unit testing"
        in prompt
    )
    assert "<input>Test message</input>" in prompt
    assert "<response_format>" in prompt
    assert "tool_call" in prompt
    assert "message" in prompt

    # Test with system prompt
    agent.system_prompt = "Test system prompt"
    prompt = agent._build_prompt("Test message")
    assert "System: Test system prompt" in prompt

    # Test with tools
    tool = MockTool()
    agent.tools = {tool.name: tool}
    prompt = agent._build_prompt("Test message")
    assert "<tools>" in prompt
    assert tool.name in prompt
    assert tool.description in prompt
    assert "Schema:" in prompt


def test_format_prompt(agent: BedrockAgent) -> None:
    """Test prompt formatting with history."""
    history = [
        Message(role="user", content="User message 1", timestamp=datetime.now()),
        Message(
            role="assistant", content="Assistant response 1", timestamp=datetime.now()
        ),
        Message(role="user", content="User message 2", timestamp=datetime.now()),
    ]

    # Test without system prompt
    prompt = agent._format_prompt("Current message", history)
    assert "User message 1" in prompt
    assert "Assistant response 1" in prompt
    assert "User message 2" in prompt
    assert "Current message" in prompt

    # Test with system prompt
    agent.system_prompt = "Test system prompt"
    prompt = agent._format_prompt("Current message", history)
    assert prompt.startswith("Test system prompt\n\n")


def test_agent_generate(agent: BedrockAgent, mock_model: MagicMock) -> None:
    """Test message generation."""
    # Test basic generation
    response = agent.generate("Test message")
    assert response["content"] == "Test response"

    # Verify model was called correctly
    mock_model.invoke.assert_called_once()
    args = mock_model.invoke.call_args[1]
    assert "Test message" in args["message"]

    # Test with tool call response
    tool_call_response = {
        "type": "tool_call",
        "tool_calls": [
            {
                "id": "call_1",
                "type": "function",
                "function": {"name": "test_tool", "arguments": {"arg": "value"}},
            }
        ],
    }
    mock_model.invoke.reset_mock()
    mock_model.invoke.return_value = tool_call_response
    response = agent.generate("Use tool")
    assert response == tool_call_response


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


def test_aws_session_initialization(mock_aws_config) -> None:
    """Test AWS session initialization."""
    with patch("boto3.Session") as mock_session:
        mock_client = MagicMock()
        mock_session.return_value.client.return_value = mock_client

        agent = BedrockAgent(
            name="test",
            model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
            role="Test agent",
        )

        # Verify session initialization
        mock_session.assert_called_once_with(
            region_name="us-west-2",
            profile_name="default",
        )

        # Test client initialization in generate method
        agent.generate("Test message")
        mock_session.return_value.client.assert_called_with(
            "bedrock-runtime",
            endpoint_url="https://bedrock-runtime.us-west-2.amazonaws.com",
        )


def test_last_token_count(agent: BedrockAgent) -> None:
    """Test last token count tracking."""
    # Initial value should be 0
    assert agent.last_token_count == 0

    # Set token count
    agent._last_token_count = 100
    assert agent.last_token_count == 100

    # Reset token count
    delattr(agent, "_last_token_count")
    assert agent.last_token_count == 0


def test_model_initialization_error() -> None:
    """Test model initialization error handling."""
    with patch("bedrock_swarm.models.factory.ModelFactory.create_model") as mock_create:
        mock_create.side_effect = ValueError("Invalid model")

        with pytest.raises(InvalidModelError, match="Invalid model"):
            BedrockAgent(
                name="test",
                model_id="invalid.model",
                role="Test agent",
            )


def test_generate_error_handling(agent: BedrockAgent, mock_model: MagicMock) -> None:
    """Test error handling in generate method."""
    # Test model invocation error
    mock_model.invoke.side_effect = Exception("Model error")

    with pytest.raises(Exception, match="Model error"):
        agent.generate("Test message")

    # Test client initialization error
    with patch.object(agent.session, "client") as mock_client:
        mock_client.side_effect = Exception("Client error")

        with pytest.raises(Exception, match="Client error"):
            agent.generate("Test message")


def test_prompt_building_with_history(agent: BedrockAgent) -> None:
    """Test prompt building with conversation history."""
    # Add messages to memory
    messages = [
        Message(
            role="user",
            content="Previous question",
            timestamp=datetime.now(),
            metadata={"type": "user_message"},
        ),
        Message(
            role="assistant",
            content="Previous answer",
            timestamp=datetime.now(),
            metadata={"type": "assistant_response"},
        ),
        Message(
            role="system",
            content="Tool result: data",
            timestamp=datetime.now(),
            metadata={"type": "tool_result", "tool_call_id": "123"},
        ),
    ]
    for msg in messages:
        agent.memory.add_message(msg)

    # Build prompt
    prompt = agent._build_prompt("Current question")

    # Verify history is included
    assert "Previous question" in prompt
    assert "Previous answer" in prompt
    assert "Tool result: data" in prompt
    assert "[Tool Result: 123]" in prompt
    assert "Current question" in prompt


def test_generate_with_memory_integration(agent: BedrockAgent) -> None:
    """Test generate method with memory integration."""
    with patch.object(agent.model, "invoke") as mock_invoke:
        # Mock model response
        mock_invoke.return_value = {"type": "message", "content": "Test response"}

        # Generate response
        agent.generate("Test message")

        # Verify message was recorded in memory
        messages = agent.memory.get_messages()
        assert len(messages) == 2  # User message and assistant response

        # Verify user message
        user_msg = next(msg for msg in messages if msg.role == "user")
        assert user_msg.content == "Test message"
        assert user_msg.metadata["type"] == "user_message"
        assert user_msg.metadata["agent"] == agent.name

        # Verify assistant response
        assistant_msg = next(msg for msg in messages if msg.role == "assistant")
        assert assistant_msg.content == "Test response"
        assert assistant_msg.metadata["type"] == "assistant_response"
        assert assistant_msg.metadata["agent"] == agent.name


def test_generate_with_tool_calls(agent: BedrockAgent) -> None:
    """Test generate method with tool calls and memory recording."""
    with patch.object(agent.model, "invoke") as mock_invoke:
        # Mock tool call response
        tool_calls = [{"id": "call_1", "name": "test_tool"}]
        mock_invoke.return_value = {"type": "tool_call", "tool_calls": tool_calls}

        # Generate response
        agent.generate("Test message")

        # Verify tool call was recorded in memory
        messages = agent.memory.get_messages()
        assert len(messages) == 2  # User message and tool call intent

        # Verify tool call message
        tool_msg = next(
            msg
            for msg in messages
            if msg.metadata and msg.metadata.get("type") == "tool_call_intent"
        )
        assert tool_msg.role == "assistant"
        assert tool_msg.metadata["tool_calls"] == tool_calls
        assert tool_msg.metadata["agent"] == agent.name


def test_memory_cleanup(agent: BedrockAgent) -> None:
    """Test memory size limits and cleanup."""
    # Add more messages than the default limit
    for i in range(1100):  # Default limit is 1000
        agent.memory.add_message(
            Message(
                role="user",
                content=f"Message {i}",
                timestamp=datetime.now(),
                metadata={"type": "user_message", "index": i},
            )
        )

    # Verify memory size is enforced
    messages = agent.memory.get_messages()
    assert len(messages) == 1000
    assert messages[0].metadata["index"] == 100  # First 100 should be removed
    assert messages[-1].metadata["index"] == 1099  # Last message should be present
