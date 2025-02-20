"""Tests for Claude model implementation."""

import json
from unittest.mock import MagicMock

import pytest

from bedrock_swarm.exceptions import ModelInvokeError, ResponseParsingError
from bedrock_swarm.models.claude import ClaudeModel


@pytest.fixture
def model() -> ClaudeModel:
    """Create a Claude model instance."""
    model = ClaudeModel("us.anthropic.claude-3-5-sonnet-20241022-v2:0")
    model.set_config(
        {
            "max_tokens": 200000,
            "default_tokens": 4096,
        }
    )
    return model


@pytest.fixture
def mock_client() -> MagicMock:
    """Create a mock Bedrock client."""
    return MagicMock()


def test_model_id(model: ClaudeModel) -> None:
    """Test model ID."""
    assert model.get_model_id() == "us.anthropic.claude-3-5-sonnet-20241022-v2:0"


def test_format_request(model: ClaudeModel) -> None:
    """Test request formatting."""
    # Basic request
    request = model.format_request(message="Test message")
    assert request == {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 4096,
        "temperature": 0.7,
        "messages": [{"role": "user", "content": "Test message"}],
    }

    # Request with system prompt and custom parameters
    request = model.format_request(
        message="Test message",
        system="Test system",
        temperature=0.5,
        max_tokens=100,
    )
    assert request == {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 100,
        "temperature": 0.5,
        "messages": [{"role": "user", "content": "Test system\n\nTest message"}],
    }

    # Test empty system prompt
    request = model.format_request(message="Test message", system="")
    assert request["messages"][0]["content"] == "Test message"


def test_extract_content(model: ClaudeModel) -> None:
    """Test content extraction from response."""
    # Test successful extraction
    mock_body = MagicMock()
    mock_body.__iter__.return_value = [
        {
            "chunk": {
                "bytes": json.dumps(
                    {
                        "type": "content_block_delta",
                        "delta": {"text": "Hello"},
                    }
                ).encode()
            }
        },
        {
            "chunk": {
                "bytes": json.dumps(
                    {
                        "type": "content_block_delta",
                        "delta": {"text": " world"},
                    }
                ).encode()
            }
        },
    ]
    response = {"body": mock_body}
    content = model._extract_content(response)
    assert content == "Hello world"

    # Test invalid JSON
    mock_body = MagicMock()
    mock_body.__iter__.return_value = [{"chunk": {"bytes": b"invalid json"}}]
    response = {"body": mock_body}
    with pytest.raises(ResponseParsingError, match="Error parsing chunk"):
        model._extract_content(response)

    # Test missing required fields
    mock_body = MagicMock()
    mock_body.__iter__.return_value = [
        {"chunk": {"bytes": json.dumps({"wrong_field": "value"}).encode()}}
    ]
    response = {"body": mock_body}
    content = model._extract_content(response)
    assert content == ""

    # Test empty response
    mock_body = MagicMock()
    mock_body.__iter__.return_value = []
    response = {"body": mock_body}
    content = model._extract_content(response)
    assert content == ""

    # Test missing chunk key
    mock_body = MagicMock()
    mock_body.__iter__.return_value = [{"not_chunk": {"bytes": b"{}"}}]
    response = {"body": mock_body}
    with pytest.raises(ResponseParsingError):
        model._extract_content(response)


def test_process_response(model: ClaudeModel) -> None:
    """Test response processing."""
    # Test message response
    mock_body = MagicMock()
    mock_body.__iter__.return_value = [
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
    response = {"body": mock_body}
    result = model.process_response(response)
    assert result == {"type": "message", "content": "Test response"}

    # Test tool call response - using content_block_delta format
    tool_call_json = {
        "type": "tool_call",
        "tool_calls": [
            {
                "id": "call_1",
                "type": "function",
                "function": {"name": "test_tool", "arguments": {"arg": "value"}},
            }
        ],
    }
    mock_body = MagicMock()
    mock_body.__iter__.return_value = [
        {
            "chunk": {
                "bytes": json.dumps(
                    {
                        "type": "content_block_delta",
                        "delta": {"text": json.dumps(tool_call_json)},
                    }
                ).encode()
            }
        }
    ]
    response = {"body": mock_body}
    result = model.process_response(response)
    assert (
        result == tool_call_json
    )  # Tool call responses are returned as-is after parsing

    # Test invalid response format
    mock_body = MagicMock()
    mock_body.__iter__.return_value = [
        {"chunk": {"bytes": json.dumps({"invalid": "format"}).encode()}}
    ]
    response = {"body": mock_body}
    result = model.process_response(response)
    assert result == {"type": "message", "content": ""}


def test_invoke(model: ClaudeModel, mock_client: MagicMock) -> None:
    """Test model invocation."""
    # Test successful invocation
    mock_stream = MagicMock()
    mock_stream.__iter__.return_value = [
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
    mock_client.invoke_model_with_response_stream.return_value = {"body": mock_stream}

    response = model.invoke(
        client=mock_client,
        message="Test message",
        system="Test system",
        temperature=0.5,
        max_tokens=100,
    )
    assert response == {"type": "message", "content": "Test response"}

    # Verify request format
    mock_client.invoke_model_with_response_stream.assert_called_once()
    call_args = mock_client.invoke_model_with_response_stream.call_args[1]
    assert call_args["modelId"] == model.get_model_id()
    request_body = json.loads(call_args["body"])
    assert request_body["messages"][0]["content"] == "Test system\n\nTest message"
    assert request_body["temperature"] == 0.5
    assert request_body["max_tokens"] == 100

    # Test client error
    mock_client.invoke_model_with_response_stream.side_effect = Exception("API error")
    with pytest.raises(ModelInvokeError, match="Error invoking model"):
        model.invoke(client=mock_client, message="Test message")


def test_token_validation(model: ClaudeModel) -> None:
    """Test token count validation."""
    # Test default tokens
    assert model.validate_token_count(None) == 4096

    # Test custom tokens within limit
    assert model.validate_token_count(1000) == 1000

    # Test exceeding limit
    with pytest.raises(ValueError, match="exceeds model's limit"):
        model.validate_token_count(300000)

    # Test with different config
    model.set_config({"max_tokens": 1000, "default_tokens": 500})
    assert model.validate_token_count(None) == 500
    with pytest.raises(ValueError, match="exceeds model's limit"):
        model.validate_token_count(1500)
