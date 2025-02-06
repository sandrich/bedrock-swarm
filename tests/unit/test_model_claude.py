"""Tests for the Claude model implementation."""

import json
from typing import Any, Dict, List, cast
from unittest.mock import MagicMock

import pytest
from botocore.exceptions import ClientError

from bedrock_swarm.exceptions import (
    ModelInvokeError,
    ResponseParsingError,
    ToolExecutionError,
)
from bedrock_swarm.models.claude import Claude35Model
from bedrock_swarm.tools.base import BaseTool


class MockTool(BaseTool):
    """Mock tool for testing."""

    def __init__(
        self, name: str = "mock_tool", description: str = "Mock tool for testing"
    ) -> None:
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
        return cast(str, self._execute_mock(**kwargs))


@pytest.fixture
def model() -> Claude35Model:
    """Create a Claude model instance for testing."""
    return Claude35Model()


@pytest.fixture
def mock_client() -> MagicMock:
    """Create a mock Bedrock client."""
    mock_client = MagicMock()

    # Set up streaming response
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

    return mock_client


def test_model_capabilities(model: Claude35Model) -> None:
    """Test model capability flags."""
    assert model.get_default_max_tokens() == 4096
    assert model.supports_tools() is True
    assert model.supports_streaming() is True


def test_format_request(model: Claude35Model) -> None:
    """Test request formatting."""
    # Test basic request
    request = model.format_request(
        message="Test message",
        system="Test system",
        temperature=0.8,
        max_tokens=1000,
    )
    assert request["anthropic_version"] == "bedrock-2023-05-31"
    assert request["temperature"] == 0.8
    assert request["max_tokens"] == 1000
    assert len(request["messages"]) == 1
    assert request["messages"][0]["role"] == "user"
    assert "Test system" in request["messages"][0]["content"]
    assert "Test message" in request["messages"][0]["content"]

    # Test request with tools
    tools: List[Dict[str, Any]] = [
        {
            "name": "test_tool",
            "description": "Test tool",
            "parameters": {"type": "object"},
        }
    ]
    request = model.format_request(
        message="Test message",
        system="Test system",
        tools=tools,
    )
    assert "test_tool" in request["messages"][0]["content"]


def test_process_message_basic(model: Claude35Model, mock_client: MagicMock) -> None:
    """Test basic message processing."""
    response = model.process_message(
        client=mock_client,
        message="Test message",
        system="Test system",
    )
    assert response == "Test response"

    # Verify request
    call_args = mock_client.invoke_model_with_response_stream.call_args[1]
    assert call_args["modelId"] == "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
    request = json.loads(call_args["body"])
    assert "Test message" in request["messages"][0]["content"]


def test_process_message_with_tools(
    model: Claude35Model, mock_client: MagicMock
) -> None:
    """Test message processing with tools."""
    # Set up tool call response
    mock_stream = MagicMock()
    mock_stream.__iter__ = MagicMock(
        return_value=iter(
            [
                {
                    "chunk": {
                        "bytes": json.dumps(
                            {
                                "type": "tool_calls",
                                "tool_calls": [
                                    {
                                        "name": "mock_tool",
                                        "parameters": {"param1": "test"},
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
                                "delta": {"text": "Final response"},
                            }
                        ).encode()
                    }
                },
            ]
        )
    )
    mock_client.invoke_model_with_response_stream.return_value = {"body": mock_stream}

    # Create tool and tool map
    tool = MockTool()
    tool_map: Dict[str, BaseTool] = {tool.name: tool}

    response = model.process_message(
        client=mock_client,
        message="Test message",
        system="Test system",
        tools=[tool.get_schema()],
        tool_map=tool_map,
    )

    assert "Mock tool executed" in response
    assert "Final response" in response
    tool._execute_mock.assert_called_once_with(param1="test")


def test_process_message_api_error(
    model: Claude35Model, mock_client: MagicMock
) -> None:
    """Test handling of API errors."""
    mock_client.invoke_model_with_response_stream.side_effect = ClientError(
        {"Error": {"Code": "500", "Message": "Test error"}}, "InvokeModel"
    )
    with pytest.raises(ModelInvokeError, match="Error invoking model"):
        model.process_message(
            client=mock_client,
            message="Test message",
            system="Test system",
        )


def test_process_message_invalid_json(
    model: Claude35Model, mock_client: MagicMock
) -> None:
    """Test handling of invalid JSON responses."""
    mock_stream = MagicMock()
    mock_stream.__iter__ = MagicMock(
        return_value=iter([{"chunk": {"bytes": b"invalid json"}}])
    )
    mock_client.invoke_model_with_response_stream.return_value = {"body": mock_stream}

    with pytest.raises(ResponseParsingError, match="Error parsing chunk"):
        model.process_message(
            client=mock_client,
            message="Test message",
            system="Test system",
        )


def test_process_message_error_chunk(
    model: Claude35Model, mock_client: MagicMock
) -> None:
    """Test handling of error chunks in response."""
    mock_stream = MagicMock()
    mock_stream.__iter__ = MagicMock(
        return_value=iter(
            [
                {
                    "chunk": {
                        "bytes": json.dumps(
                            {
                                "type": "error",
                                "message": "Test error",
                            }
                        ).encode()
                    }
                }
            ]
        )
    )
    mock_client.invoke_model_with_response_stream.return_value = {"body": mock_stream}

    with pytest.raises(ModelInvokeError, match="Test error"):
        model.process_message(
            client=mock_client,
            message="Test message",
            system="Test system",
        )


def test_process_message_tool_error(
    model: Claude35Model, mock_client: MagicMock
) -> None:
    """Test handling of tool execution errors."""
    # Create tool that raises error
    error_tool = MockTool(name="error_tool")
    error_tool._execute_mock.side_effect = Exception("Tool execution failed")
    tool_map: Dict[str, BaseTool] = {"error_tool": error_tool}

    # Set up response with tool call
    mock_stream = MagicMock()
    mock_stream.__iter__ = MagicMock(
        return_value=iter(
            [
                {
                    "chunk": {
                        "bytes": json.dumps(
                            {
                                "type": "tool_calls",
                                "tool_calls": [
                                    {
                                        "name": "error_tool",
                                        "parameters": {"param1": "test"},
                                    }
                                ],
                            }
                        ).encode()
                    }
                }
            ]
        )
    )
    mock_client.invoke_model_with_response_stream.return_value = {"body": mock_stream}

    with pytest.raises(ToolExecutionError, match="Error executing tool error_tool"):
        model.process_message(
            client=mock_client,
            message="Test message",
            system="Test system",
            tools=[error_tool.get_schema()],
            tool_map=tool_map,
        )


def test_parse_stream_chunk(model: Claude35Model) -> None:
    """Test parsing of stream chunks."""
    # Test content chunk
    chunk = {
        "type": "content_block_delta",
        "delta": {"text": "Test content"},
    }
    assert model.parse_stream_chunk(chunk) == "Test content"

    # Test non-content chunk
    chunk = {
        "type": "other",
        "data": "Test data",
    }
    assert model.parse_stream_chunk(chunk) is None

    # Test empty chunk
    chunk = {}
    assert model.parse_stream_chunk(chunk) is None
