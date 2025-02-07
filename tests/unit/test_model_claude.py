"""Tests for Claude model implementation."""

import json
from unittest.mock import MagicMock

import pytest

from bedrock_swarm.exceptions import ModelInvokeError, ResponseParsingError
from bedrock_swarm.models.claude import Claude35Model


@pytest.fixture
def model() -> Claude35Model:
    """Create a Claude model instance."""
    return Claude35Model()


@pytest.fixture
def mock_client() -> MagicMock:
    """Create a mock Bedrock client."""
    return MagicMock()


def test_model_id(model: Claude35Model) -> None:
    """Test model ID."""
    assert model.get_model_id() == "us.anthropic.claude-3-5-sonnet-20241022-v2:0"


def test_format_request(model: Claude35Model) -> None:
    """Test request formatting."""
    # Basic request
    request = model.format_request(message="Test message")
    assert request == {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 4096,
        "temperature": 0.7,
        "messages": [{"role": "user", "content": "Test message"}],
    }

    # Request with system prompt
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


def test_invoke_basic(model: Claude35Model, mock_client: MagicMock) -> None:
    """Test basic model invocation."""
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
    mock_client.invoke_model_with_response_stream.return_value = {"body": mock_stream}

    response = model.invoke(
        client=mock_client,
        message="Test message",
        system="Test system",
    )
    assert response["content"] == "Test response"


def test_invoke_invalid_json(model: Claude35Model, mock_client: MagicMock) -> None:
    """Test handling of invalid JSON responses."""
    mock_stream = MagicMock()
    mock_stream.__iter__ = MagicMock(
        return_value=iter([{"chunk": {"bytes": b"invalid json"}}])
    )
    mock_client.invoke_model_with_response_stream.return_value = {"body": mock_stream}

    with pytest.raises(ModelInvokeError, match="Error invoking model"):
        model.invoke(
            client=mock_client,
            message="Test message",
            system="Test system",
        )


def test_invoke_error_chunk(model: Claude35Model, mock_client: MagicMock) -> None:
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

    response = model.invoke(
        client=mock_client,
        message="Test message",
        system="Test system",
    )
    assert response["content"] == ""


def test_process_response_with_invalid_json(model: Claude35Model) -> None:
    """Test response processing with invalid JSON."""
    mock_response = {
        "body": MagicMock(
            __iter__=MagicMock(
                return_value=iter([{"chunk": {"bytes": b"invalid json"}}])
            )
        )
    }

    with pytest.raises(ResponseParsingError, match="Error parsing chunk"):
        model.process_response(mock_response)


def test_process_response(model: Claude35Model) -> None:
    """Test response processing."""
    mock_response = {
        "body": MagicMock(
            __iter__=MagicMock(
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
        )
    }

    result = model.process_response(mock_response)
    assert result["content"] == "Test response"
