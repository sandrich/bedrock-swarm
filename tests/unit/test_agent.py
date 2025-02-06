"""Tests for the agent functionality."""

# mypy: ignore-errors

import json
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock, patch

import pytest
from botocore.exceptions import ClientError

from bedrock_swarm.agents.base import BedrockAgent
from bedrock_swarm.config import AWSConfig
from bedrock_swarm.exceptions import InvalidModelError, ModelInvokeError, ToolError
from bedrock_swarm.memory.base import SimpleMemory
from bedrock_swarm.models.base import BedrockModel
from bedrock_swarm.tools.base import BaseTool
from bedrock_swarm.tools.factory import ToolFactory


class MockTool(BaseTool):
    """Mock tool for testing."""

    def __init__(
        self, name: str = "mock_tool", description: str = "Mock tool for testing"
    ):
        """Initialize mock tool."""
        self._name = name
        self._description = description
        self._execute_mock = MagicMock(return_value="Mock tool executed")

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
        return self._execute_mock(**kwargs)


class MockModel(BedrockModel):
    """Mock model for testing."""

    def __init__(self):
        """Initialize mock model."""
        self._last_token_count = 0

    def get_default_max_tokens(self) -> int:
        """Get the default maximum tokens."""
        return 4096

    def supports_tools(self) -> bool:
        """Check if the model supports tools."""
        return True

    def supports_streaming(self) -> bool:
        """Check if the model supports streaming."""
        return True

    def process_message(
        self,
        client: Any,
        message: str,
        system: str,
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        tool_map: Optional[Dict[str, BaseTool]] = None,
    ) -> str:
        """Process a message."""
        # Use the client's invoke_model_with_response_stream method
        try:
            request = self.format_request(
                messages=[{"role": "user", "content": message}],
                tool_map=tool_map,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            # We don't need to store the response since we're returning a fixed string
            client.invoke_model_with_response_stream(
                modelId="test.model",
                body=json.dumps(request),
            )
            # Set token count
            self._last_token_count = 50  # 10 input + 40 output tokens
            return "Test response"
        except ClientError as e:
            raise ModelInvokeError(str(e))

    def format_request(
        self,
        messages: List[Dict[str, Any]],
        tool_map: Optional[Dict[str, BaseTool]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Format a request."""
        return {"prompt": "Mock prompt"}

    def parse_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse a response."""
        return {"response": "Mock response"}

    def parse_stream_chunk(self, chunk: Dict[str, Any]) -> Dict[str, Any]:
        """Parse a stream chunk."""
        return {"response": "Mock chunk response"}

    @property
    def last_token_count(self) -> int:
        """Get the token count from the last request."""
        return self._last_token_count


@pytest.fixture(autouse=True)
def mock_model_factory():
    """Mock the model factory for all tests."""
    with patch("bedrock_swarm.models.factory.ModelFactory.create_model") as mock:
        mock.return_value = MockModel()
        yield mock


@pytest.fixture(autouse=True)
def clear_tool_registry() -> None:
    """Clear tool registry before each test."""
    ToolFactory.clear()
    yield
    ToolFactory.clear()


@pytest.fixture
def mock_bedrock_client() -> MagicMock:
    """Create a mock Bedrock client."""
    mock_client = MagicMock()

    # Set up mock response
    mock_stream = MagicMock()
    mock_stream.__iter__ = MagicMock(
        return_value=iter(
            [
                {
                    "chunk": {
                        "bytes": json.dumps(
                            {
                                "type": "content_block_delta",
                                "delta": {"text": "Test response"},
                                "usage": {"input_tokens": 10, "output_tokens": 40},
                            }
                        ).encode()
                    }
                }
            ]
        )
    )
    mock_stream.close = MagicMock()

    mock_client.invoke_model_with_response_stream = MagicMock(
        return_value={"body": mock_stream}
    )

    # Patch the session client
    with patch("boto3.Session.client") as mock_session_client:
        mock_session_client.return_value = mock_client
        yield mock_client


@pytest.fixture
def mock_tool() -> MockTool:
    """Create a mock tool for testing."""
    return MockTool()


@pytest.fixture
def agent() -> BedrockAgent:
    """Create a BedrockAgent instance for testing."""
    config = AWSConfig(region="us-west-2", profile="default")
    agent = BedrockAgent(
        name="test_agent",
        model_id="test.model",
        instructions="Test instructions",
        aws_config=config,
    )
    return agent


def test_init_basic(agent: BedrockAgent) -> None:
    """Test basic initialization of BedrockAgent."""
    assert agent.name == "test_agent"
    assert agent.model_id == "test.model"
    assert agent.instructions == "Test instructions"
    assert agent.temperature == 0.7  # Default temperature
    assert agent.max_tokens is not None


def test_agent_process_message_basic(
    agent: BedrockAgent, mock_bedrock_client: MagicMock
) -> None:
    """Test basic message processing functionality of BedrockAgent."""
    response = agent.process_message("Test message")
    assert response == "Test response"
    assert agent.last_token_count == 50  # 10 input + 40 output tokens


def test_add_tool(agent: BedrockAgent, mock_tool: MockTool) -> None:
    """Test adding a tool to the agent."""
    agent.add_tool(mock_tool)
    assert mock_tool.name in agent._tools
    assert agent._tools[mock_tool.name] == mock_tool


def test_remove_tool(agent: BedrockAgent, mock_tool: MockTool) -> None:
    """Test removing a tool from the agent."""
    agent.add_tool(mock_tool)
    agent.remove_tool(mock_tool.name)
    assert mock_tool.name not in agent._tools


def test_get_tool(agent: BedrockAgent, mock_tool: MockTool) -> None:
    """Test getting a tool from the agent."""
    agent.add_tool(mock_tool)
    retrieved_tool = agent.get_tool(mock_tool.name)
    assert retrieved_tool == mock_tool


def test_get_nonexistent_tool(agent: BedrockAgent) -> None:
    """Test getting a nonexistent tool."""
    with pytest.raises(ToolError, match="Tool 'nonexistent_tool' not found"):
        agent.get_tool("nonexistent_tool")


def test_process_message_with_memory(
    agent: BedrockAgent, mock_bedrock_client: MagicMock
) -> None:
    """Test processing a message with memory enabled."""
    memory = SimpleMemory(max_size=5)
    agent.memory = memory
    response = agent.process_message("Test message")
    assert isinstance(response, str)
    assert len(response) > 0
    messages = memory.get_messages()
    assert len(messages) == 2  # Human message + assistant response


def test_agent_validate_temperature() -> None:
    """Test temperature validation."""
    config = AWSConfig(region="us-west-2", profile="default")

    # Valid temperatures
    agent = BedrockAgent(
        name="test",
        model_id="test.model",
        aws_config=config,
        temperature=0.5,
    )
    assert agent.temperature == 0.5

    # Invalid temperatures
    with pytest.raises(ValueError):
        BedrockAgent(
            name="test",
            model_id="test.model",
            aws_config=config,
            temperature=1.5,
        )

    with pytest.raises(ValueError):
        BedrockAgent(
            name="test",
            model_id="test.model",
            aws_config=config,
            temperature=-0.5,
        )


def test_agent_validate_model_id(mock_model_factory: MagicMock) -> None:
    """Test model ID validation."""
    config = AWSConfig(region="us-west-2", profile="default")

    # Valid model ID
    agent = BedrockAgent(
        name="test",
        model_id="test.model",
        aws_config=config,
    )
    assert agent.model_id == "test.model"

    # Test invalid model ID
    mock_model_factory.side_effect = ValueError("Invalid model")
    with pytest.raises(InvalidModelError):
        BedrockAgent(
            name="test",
            model_id="invalid_model",
            aws_config=config,
        )


def test_agent_tool_management() -> None:
    """Test comprehensive tool management."""
    config = AWSConfig(region="us-west-2", profile="default")
    agent = BedrockAgent(
        name="test",
        model_id="test.model",
        aws_config=config,
    )

    # Add tools
    tool1 = MockTool(name="tool1")
    tool2 = MockTool(name="tool2")
    agent.add_tool(tool1)
    agent.add_tool(tool2)

    # Verify tools were added
    assert len(agent.tools) == 2
    assert "tool1" in agent._tools
    assert "tool2" in agent._tools

    # Get tools
    retrieved_tool = agent.get_tool("tool1")
    assert retrieved_tool == tool1

    # Remove tool
    agent.remove_tool("tool1")
    assert "tool1" not in agent._tools
    assert len(agent.tools) == 1

    # Clear tools
    agent.clear_tools()
    assert len(agent.tools) == 0
    assert not agent._tools


def test_agent_memory_management() -> None:
    """Test memory management functionality."""
    config = AWSConfig(region="us-west-2", profile="default")
    agent = BedrockAgent(
        name="test",
        model_id="test.model",
        aws_config=config,
    )

    # Test default memory
    assert isinstance(agent.memory, SimpleMemory)

    # Test custom memory
    custom_memory = SimpleMemory(max_size=10)
    agent.memory = custom_memory
    assert agent.memory == custom_memory

    # Test memory persistence
    with patch.object(agent.model, "process_message", return_value="Test response"):
        agent.process_message("Test input")
        messages = agent.memory.get_messages()
        assert len(messages) == 2  # Input and response
        assert messages[0].content == "Test input"
        assert messages[1].content == "Test response"


def test_agent_generate(agent: BedrockAgent, mock_bedrock_client: MagicMock) -> None:
    """Test the generate method."""
    result = agent.generate("Test message")
    assert isinstance(result, dict)
    assert "response" in result
    assert result["response"] == "Test response"

    # Test with tool results
    tool_results = [{"tool": "test_tool", "result": "test_result"}]
    result = agent.generate("Test message", tool_results=tool_results)
    assert isinstance(result, dict)
    assert "response" in result
    assert result["response"] == "Test response"
