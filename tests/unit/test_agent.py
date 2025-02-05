"""Tests for the agent functionality."""

# mypy: ignore-errors

import json
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from botocore.exceptions import ClientError

from bedrock_swarm.agents.base import BedrockAgent
from bedrock_swarm.config import AWSConfig
from bedrock_swarm.exceptions import (
    InvalidModelError,
    ModelInvokeError,
    ResponseParsingError,
    ToolError,
    ToolExecutionError,
)
from bedrock_swarm.memory.base import SimpleMemory
from bedrock_swarm.tools.base import BaseTool
from bedrock_swarm.tools.factory import ToolFactory
from bedrock_swarm.tools.web import WebSearchTool


class MockTool(BaseTool):
    """Mock tool for testing."""

    def __init__(self, name="mock_tool"):
        """Initialize mock tool."""
        super().__init__(name=name)
        self.execute = MagicMock(return_value="Mock tool executed")

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

    # Standard response mock for Claude
    mock_response = {
        "completion": "Test response",
        "stop_reason": "stop",
    }
    mock_body = MagicMock()
    mock_body.read = MagicMock(return_value=json.dumps(mock_response).encode())
    mock_client.invoke_model = MagicMock(return_value={"body": mock_body})

    # Streaming response mock for Claude 3
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

    # Patch the client creation
    with patch("boto3.Session") as mock_session:
        session = MagicMock()
        session.client = MagicMock(return_value=mock_client)
        mock_session.return_value = session
        yield mock_client


@pytest.fixture
def mock_tool() -> MockTool:
    """Create a mock tool for testing."""
    return MockTool(name="mock_tool")


@pytest.fixture
def agent() -> BedrockAgent:
    """Create a BedrockAgent instance for testing."""
    config = AWSConfig(region="us-west-2", profile="default")
    agent = BedrockAgent(
        name="test_agent",
        model_id="anthropic.claude-v2",
        instructions="Test instructions",
        aws_config=config,
    )
    return agent


def test_init_basic(agent: BedrockAgent) -> None:
    """Test basic initialization of BedrockAgent."""
    assert agent.name == "test_agent"
    assert agent.model_id == "anthropic.claude-v2"
    assert agent.instructions == "Test instructions"


def test_agent_process_message_basic():
    """Test basic message processing functionality of BedrockAgent."""
    # Create AWS config
    aws_config = AWSConfig(region="us-west-2", profile="default")

    # Create the agent with proper parameters
    agent = BedrockAgent(
        name="test_agent",
        model_id="anthropic.claude-v2",
        aws_config=aws_config,
        instructions="You are a helpful assistant.",
    )

    # Create mock response
    mock_response = {
        "body": MagicMock(
            read=MagicMock(
                return_value=json.dumps(
                    {"completion": "Test response", "stop_reason": "stop"}
                ).encode()
            )
        )
    }

    # Create mock bedrock client
    mock_bedrock = MagicMock()
    mock_bedrock.invoke_model = MagicMock(return_value=mock_response)

    # Create mock session that returns the client
    mock_session = MagicMock()
    mock_session.client = MagicMock(return_value=mock_bedrock)

    # Replace the agent's session
    agent.session = mock_session

    # Process message
    response = agent.process_message("Test message")

    # Verify response
    assert response == "Test response"

    # Verify client was created with correct parameters
    mock_session.client.assert_called_once_with("bedrock-runtime", endpoint_url=None)

    # Verify model was invoked with correct parameters
    mock_bedrock.invoke_model.assert_called_once()


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


def test_process_message_with_memory(agent: BedrockAgent) -> None:
    """Test processing a message with memory enabled."""
    memory = SimpleMemory(max_size=5)
    setattr(agent, "memory", memory)  # type: ignore
    response = agent.process_message("Test message")
    assert isinstance(response, str)
    assert len(response) > 0
    messages = memory.get_messages()
    assert len(messages) > 0


def test_agent_process_message_claude(
    agent: BedrockAgent, mock_bedrock_client: MagicMock
) -> None:
    """Tests that agent can process message with Claude model."""
    mock_response = {
        "completion": "Test response",
        "stop_reason": "stop",
    }

    mock_body = MagicMock()
    mock_body.read = MagicMock(return_value=json.dumps(mock_response).encode())

    mock_bedrock_client.invoke_model = MagicMock(return_value={"body": mock_body})

    response = agent.process_message("Test message")
    assert response == "Test response"


def test_agent_process_message_titan() -> None:
    """Tests that agent can process message with Titan model."""
    config = AWSConfig(region="us-west-2", profile="default")
    mock_client = MagicMock()
    mock_response = {"results": [{"outputText": "Test response"}]}

    mock_body = MagicMock()
    mock_body.read = MagicMock(return_value=json.dumps(mock_response).encode())

    mock_client.invoke_model = MagicMock(return_value={"body": mock_body})

    with patch("boto3.Session") as mock_session:
        session = MagicMock()
        session.client.return_value = mock_client
        mock_session.return_value = session

        agent = BedrockAgent(
            name="titan_agent",
            model_id="amazon.titan-text-express-v1",
            aws_config=config,
        )

        response = agent.process_message("Test message")
        assert response == "Test response"


def test_agent_process_message_jurassic() -> None:
    """Tests that agent can process message with Jurassic model."""
    config = AWSConfig(region="us-west-2", profile="default")
    mock_client = MagicMock()
    mock_response = {"text": "Test response"}

    mock_body = MagicMock()
    mock_body.read = MagicMock(return_value=json.dumps(mock_response).encode())

    mock_client.invoke_model = MagicMock(return_value={"body": mock_body})

    with patch("boto3.Session") as mock_session:
        session = MagicMock()
        session.client.return_value = mock_client
        mock_session.return_value = session

        agent = BedrockAgent(
            name="jurassic_agent", model_id="ai21.j2-ultra-v1", aws_config=config
        )

        response = agent.process_message("Test message")
        assert response == "Test response"


def test_agent_process_message_cohere() -> None:
    """Tests that agent can process message with Cohere model."""
    config = AWSConfig(region="us-west-2", profile="default")
    mock_client = MagicMock()
    mock_response = {"text": "Test response"}

    mock_body = MagicMock()
    mock_body.read = MagicMock(return_value=json.dumps(mock_response).encode())

    mock_client.invoke_model = MagicMock(return_value={"body": mock_body})

    with patch("boto3.Session") as mock_session:
        session = MagicMock()
        session.client.return_value = mock_client
        mock_session.return_value = session

        agent = BedrockAgent(
            name="cohere_agent", model_id="cohere.command-text-v14", aws_config=config
        )

        response = agent.process_message("Test message")
        assert response == "Test response"


def test_agent_response_fallback() -> None:
    """Tests that agent can handle unexpected response formats."""
    config = AWSConfig(region="us-west-2", profile="default")
    mock_client = MagicMock()
    mock_response = {"unexpected_key": {"text": "Test response"}}

    mock_body = MagicMock()
    mock_body.read = MagicMock(return_value=json.dumps(mock_response).encode())

    mock_client.invoke_model = MagicMock(return_value={"body": mock_body})

    with patch("boto3.Session") as mock_session:
        session = MagicMock()
        session.client.return_value = mock_client
        mock_session.return_value = session

        agent = BedrockAgent(
            name="fallback_agent", model_id="anthropic.claude-v2", aws_config=config
        )

        with pytest.raises(ResponseParsingError):
            agent.process_message("Test message")


def test_agent_process_message_with_system_prompt(
    agent: BedrockAgent, mock_bedrock_client: MagicMock
) -> None:
    """Tests that agent includes system prompt in process_message."""
    mock_response = {
        "completion": "Test response",
        "stop_reason": "stop",
    }

    mock_body = MagicMock()
    mock_body.read = MagicMock(return_value=json.dumps(mock_response).encode())

    mock_bedrock_client.invoke_model = MagicMock(return_value={"body": mock_body})

    agent.process_message("Test message")

    # Verify system prompt was included
    call_args = mock_bedrock_client.invoke_model.call_args[1]
    assert "Test instructions" in call_args["body"]


def test_agent_process_message_with_tools(
    agent: BedrockAgent, mock_bedrock_client: MagicMock
) -> None:
    """Tests that agent can process messages with tools (Claude only)."""
    # Add tool to agent
    tool = MockTool(name="mock_tool")
    agent.add_tool(tool)

    # Set up mock response
    mock_response = {
        "completion": "Test response with tool call",
        "stop_reason": "stop_sequence",
        "tool_calls": [
            {
                "type": "function",
                "function": {
                    "name": "mock_tool",
                    "arguments": '{"param1": "value1", "param2": 1}',
                },
            }
        ],
    }

    mock_body = MagicMock()
    mock_body.read = MagicMock(return_value=json.dumps(mock_response).encode())

    mock_bedrock_client.invoke_model = MagicMock(return_value={"body": mock_body})

    # Process message
    response = agent.process_message("Test message")
    assert "Mock tool executed" in response
    assert tool.execute.called


def test_agent_process_message_with_tools_non_claude() -> None:
    """Tests that tools are ignored for non-Claude models."""
    config = AWSConfig(region="us-west-2", profile="default")
    mock_client = MagicMock()
    mock_response = {"results": [{"outputText": "Test response"}]}

    mock_body = MagicMock()
    mock_body.read = MagicMock(return_value=json.dumps(mock_response).encode())

    mock_client.invoke_model = MagicMock(return_value={"body": mock_body})

    with patch("boto3.Session") as mock_session:
        session = MagicMock()
        session.client.return_value = mock_client
        mock_session.return_value = session

        agent = BedrockAgent(
            name="titan_agent",
            model_id="amazon.titan-text-express-v1",
            aws_config=config,
        )

        # Add tool to agent
        tool = MockTool(name="mock_tool")
        agent.add_tool(tool)

        # Process message
        response = agent.process_message("Test message")
        assert response == "Test response"
        assert not tool.execute.called


def test_agent_api_error(agent: BedrockAgent, mock_bedrock_client: MagicMock) -> None:
    """Tests that agent process_message fails with API error."""
    mock_bedrock_client.invoke_model.side_effect = ClientError(
        error_response={"Error": {"Code": "ThrottlingException"}},
        operation_name="InvokeModel",
    )

    with pytest.raises(ModelInvokeError):
        agent.process_message("Test message")


def test_agent_invalid_response(
    agent: BedrockAgent, mock_bedrock_client: MagicMock
) -> None:
    """Tests that agent process_message fails with invalid response."""
    mock_response = {"invalid": "response"}
    mock_bedrock_client.invoke_model.return_value = {
        "body": MagicMock(
            read=MagicMock(return_value=json.dumps(mock_response).encode())
        )
    }

    with pytest.raises(ResponseParsingError):
        agent.process_message("Test message")


def test_agent_invalid_json(
    agent: BedrockAgent, mock_bedrock_client: MagicMock
) -> None:
    """Tests that agent process_message fails with invalid JSON."""
    mock_body = MagicMock()
    mock_body.read = MagicMock(return_value=b"invalid json")

    mock_bedrock_client.invoke_model = MagicMock(return_value={"body": mock_body})

    with pytest.raises(ResponseParsingError):
        agent.process_message("Test message")


def test_agent_tool_execution_error(agent, mock_bedrock_client):
    """Tests that agent fails when tool execution fails."""
    # Create a mock tool that raises an error
    tool = MockTool(name="mock_tool")
    tool.execute = MagicMock(side_effect=ToolExecutionError("Tool execution failed"))
    agent.add_tool(tool)

    # Set up mock response with tool call
    mock_response = {
        "completion": "Test response with tool call",
        "stop_reason": "stop_sequence",
        "tool_calls": [
            {
                "type": "function",
                "function": {
                    "name": "mock_tool",
                    "arguments": '{"param1": "value1", "param2": 1}',
                },
            }
        ],
    }

    mock_body = MagicMock()
    mock_body.read = MagicMock(return_value=json.dumps(mock_response).encode())

    mock_bedrock_client.invoke_model = MagicMock(return_value={"body": mock_body})

    with pytest.raises(ToolExecutionError, match="Tool execution failed"):
        agent.process_message("Test message")


def test_add_tool_by_name(agent: BedrockAgent) -> None:
    """Tests adding a tool by name."""
    tool = agent.add_tool("WebSearchTool")
    assert isinstance(tool, WebSearchTool)
    assert tool.name in agent._tools
    assert agent._tools[tool.name] == tool


def test_add_invalid_tool_type(agent: BedrockAgent) -> None:
    """Tests adding an invalid tool type."""
    with pytest.raises(ToolError):
        agent.add_tool("InvalidTool")


def test_agent_process_message_claude_3(
    agent: BedrockAgent, mock_bedrock_client: MagicMock
) -> None:
    """Tests that agent can process message with Claude 3.5 model."""
    # Update agent to use Claude 3.5
    agent.model_id = "anthropic.claude-3-sonnet-20240229-v1:0"

    # Process message and verify response
    response = agent.process_message("Test message")
    assert response == "Test response"

    # Verify streaming endpoint was called
    mock_bedrock_client.invoke_model_with_response_stream.assert_called_once()

    # Verify stream was properly closed
    stream = mock_bedrock_client.invoke_model_with_response_stream.return_value["body"]
    stream.close.assert_called_once()


def test_agent_process_message_with_function_call(agent, mock_bedrock_client):
    """Tests that agent can process function calls in the new format."""
    # Add tool to agent
    tool = MockTool(name="mock_tool")
    agent.add_tool(tool)

    # Set up mock response with function call
    mock_response = {
        "completion": "Test response with tool call",
        "stop_reason": "stop",
        "tool_calls": [
            {
                "type": "function",
                "function": {
                    "name": "mock_tool",
                    "arguments": '{"param1": "value1", "param2": 1}',
                },
            }
        ],
    }

    mock_body = MagicMock()
    mock_body.read = MagicMock(return_value=json.dumps(mock_response).encode())

    mock_bedrock_client.invoke_model = MagicMock(return_value={"body": mock_body})

    response = agent.process_message("Test message")
    assert "Mock tool executed" in response
    assert tool.execute.called


def test_agent_process_message_with_function_call_claude_3(
    agent: BedrockAgent, mock_bedrock_client: MagicMock
) -> None:
    """Tests that agent can process function calls with Claude 3.5."""
    # Update agent to use Claude 3.5
    agent.model_id = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"

    # Add tool to agent
    tool = MockTool(name="mock_tool")
    agent.add_tool(tool)

    # Set up streaming response with tool call
    mock_stream = MagicMock()
    mock_stream.__iter__ = MagicMock()
    mock_stream.__iter__.return_value = iter(
        [
            {
                "chunk": {
                    "bytes": json.dumps(
                        {
                            "type": "content_block_delta",
                            "delta": {"text": "Let me try that for you."},
                        }
                    ).encode()
                }
            },
            {
                "chunk": {
                    "bytes": json.dumps(
                        {
                            "type": "tool_calls",
                            "tool_calls": [
                                {
                                    "name": "mock_tool",
                                    "parameters": {"param1": "value1", "param2": 1},
                                }
                            ],
                        }
                    ).encode()
                }
            },
            {
                "chunk": {
                    "bytes": json.dumps(
                        {
                            "type": "content_block_delta",
                            "delta": {"text": " Here's the result."},
                        }
                    ).encode()
                }
            },
        ]
    )
    mock_stream.close = MagicMock()

    mock_bedrock_client.invoke_model_with_response_stream = MagicMock(
        return_value={"body": mock_stream}
    )

    response = agent.process_message("Use the test tool")
    assert "Mock tool executed" in response


def test_agent_process_message_with_streaming_error(agent, mock_bedrock_client):
    """Tests handling of streaming errors with Claude 3.5."""
    # Update agent to use Claude 3.5
    agent.model_id = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"

    # Mock streaming error
    mock_stream = MagicMock()
    mock_stream.__iter__ = MagicMock()
    mock_stream.__iter__.return_value = iter(
        [
            {
                "chunk": {
                    "bytes": json.dumps(
                        {"type": "error", "message": "Stream error"}
                    ).encode()
                }
            }
        ]
    )
    mock_stream.close = MagicMock()

    mock_bedrock_client.invoke_model_with_response_stream = MagicMock(
        return_value={"body": mock_stream}
    )

    with pytest.raises(ModelInvokeError, match="Stream error"):
        agent.process_message("Test message")


def test_agent_process_message_with_invalid_chunk(agent, mock_bedrock_client):
    """Tests handling of invalid chunks in streaming response."""
    # Update agent to use Claude 3.5
    agent.model_id = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"

    # Set up streaming response with invalid chunk
    mock_stream = MagicMock()
    mock_stream.__iter__ = MagicMock()
    mock_stream.__iter__.return_value = iter([{"chunk": {"bytes": b"invalid json"}}])
    mock_stream.close = MagicMock()

    mock_bedrock_client.invoke_model_with_response_stream = MagicMock(
        return_value={"body": mock_stream}
    )

    with pytest.raises(ResponseParsingError):
        agent.process_message("Test message")


def test_agent_validate_temperature() -> None:
    """Tests temperature validation."""
    config = AWSConfig(region="us-west-2", profile="default")

    # Test default temperature
    with patch("boto3.Session"):
        agent = BedrockAgent(
            name="test_agent", model_id="anthropic.claude-v2", aws_config=config
        )
        assert agent.temperature == 0.7

    # Test valid temperature
    with patch("boto3.Session"):
        agent = BedrockAgent(
            name="test_agent",
            model_id="anthropic.claude-v2",
            aws_config=config,
            temperature=0.5,
        )
        assert agent.temperature == 0.5

    # Test invalid temperature
    with patch("boto3.Session"), pytest.raises(ValueError):
        BedrockAgent(
            name="test_agent",
            model_id="anthropic.claude-v2",
            aws_config=config,
            temperature=1.5,
        )


def test_agent_validate_model_id() -> None:
    """Tests model ID validation."""
    config = AWSConfig(region="us-west-2", profile="default")

    # Test valid model IDs
    valid_models = [
        "anthropic.claude-v2",
        "amazon.titan-text-express-v1",
        "ai21.j2-ultra-v1",
        "cohere.command-text-v14",
        "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    ]

    for model_id in valid_models:
        with patch("boto3.Session"):
            agent = BedrockAgent(
                name="test_agent", model_id=model_id, aws_config=config
            )
            assert agent.model_id == model_id

    # Test invalid model family
    with (
        patch("boto3.Session"),
        pytest.raises(InvalidModelError, match="Unsupported model family"),
    ):
        BedrockAgent(name="test_agent", model_id="invalid.model-v1", aws_config=config)

    # Test invalid version
    with (
        patch("boto3.Session"),
        pytest.raises(InvalidModelError, match="Unsupported version"),
    ):
        BedrockAgent(
            name="test_agent", model_id="anthropic.claude-invalid", aws_config=config
        )


def test_agent_tool_management() -> None:
    """Tests tool management methods."""
    config = AWSConfig(region="us-west-2", profile="default")

    with patch("boto3.Session"):
        agent = BedrockAgent(
            name="test_agent", model_id="anthropic.claude-v2", aws_config=config
        )

        # Test adding tool
        tool = MockTool(name="mock_tool")
        added_tool = agent.add_tool(tool)
        assert added_tool == tool
        assert tool.name in agent._tools

        # Test getting tool
        retrieved_tool = agent.get_tool(tool.name)
        assert retrieved_tool == tool

        # Test getting nonexistent tool
        with pytest.raises(ToolError):
            agent.get_tool("nonexistent")

        # Test getting all tools
        tools = agent.get_tools()
        assert isinstance(tools, dict)
        assert tool.name in tools
        assert tools[tool.name] == tool

        # Test removing tool
        agent.remove_tool(tool.name)
        assert tool.name not in agent._tools

        # Test removing nonexistent tool
        with pytest.raises(ToolError):
            agent.remove_tool("nonexistent")

        # Test clearing tools
        agent.add_tool(tool)
        assert len(agent._tools) > 0
        agent.clear_tools()
        assert len(agent._tools) == 0


def test_agent_process_message_with_tool_call_error_claude_3(
    agent: BedrockAgent, mock_bedrock_client: MagicMock
) -> None:
    """Tests that agent can handle tool call errors with Claude 3.5."""
    # Update agent to use Claude 3.5
    agent.model_id = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"

    # Add tool that raises an error
    class ErrorTool(BaseTool):
        def __init__(self, name: str, description: str) -> None:
            self._name = name
            self._description = description
            super().__init__(name=name, description=description)
            self.execute = MagicMock(side_effect=Exception("Tool execution failed"))

        @property
        def name(self) -> str:
            return self._name

        @property
        def description(self) -> str:
            return self._description

        def _execute_impl(self, *args: Any, **kwargs: Any) -> str:
            raise Exception("Tool execution failed")

        def get_schema(self):
            return {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "param1": {"type": "string"},
                        "param2": {"type": "integer"},
                    },
                    "required": ["param1"],
                },
            }

    tool = ErrorTool(name="error_tool", description="Test tool that raises error")
    agent.add_tool(tool)

    # Set up streaming response with tool call
    mock_stream = MagicMock()
    mock_stream.__iter__ = MagicMock()
    mock_stream.__iter__.return_value = iter(
        [
            {
                "chunk": {
                    "bytes": json.dumps(
                        {
                            "type": "content_block_delta",
                            "delta": {"text": "Let me try that for you."},
                        }
                    ).encode()
                }
            },
            {
                "chunk": {
                    "bytes": json.dumps(
                        {
                            "type": "tool_calls",
                            "tool_calls": [
                                {
                                    "name": "error_tool",
                                    "parameters": {"param1": "value1", "param2": 1},
                                }
                            ],
                        }
                    ).encode()
                }
            },
            {
                "chunk": {
                    "bytes": json.dumps(
                        {
                            "type": "content_block_delta",
                            "delta": {"text": " I encountered an error."},
                        }
                    ).encode()
                }
            },
        ]
    )
    mock_stream.close = MagicMock()

    mock_bedrock_client.invoke_model_with_response_stream = MagicMock(
        return_value={"body": mock_stream}
    )

    response = agent.process_message("Use the error tool")
    assert "Tool execution failed" in response
