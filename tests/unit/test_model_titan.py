"""Tests for Titan model implementation."""

import json
from unittest.mock import MagicMock, patch

import pytest
from botocore.exceptions import ClientError

from bedrock_swarm.exceptions import ModelInvokeError
from bedrock_swarm.models.factory import ModelFactory
from bedrock_swarm.models.titan import TitanModel


def test_model_initialization():
    """Test model initialization with valid and invalid model IDs."""
    # Valid model ID
    model = ModelFactory.create_model("amazon.titan-text-express-v1")
    assert isinstance(model, TitanModel)
    assert model.get_model_id() == "amazon.titan-text-express-v1"

    # Invalid model ID
    with pytest.raises(ValueError, match="Unsupported model family"):
        ModelFactory.create_model("invalid.model-id")

    # Valid family but invalid version
    with pytest.raises(ValueError, match="Unsupported version"):
        ModelFactory.create_model("amazon.titan-text-express-v999")


@pytest.mark.parametrize(
    "model_id,max_tokens,should_raise",
    [
        ("amazon.titan-text-express-v1", 8000, False),  # At limit
        ("amazon.titan-text-express-v1", 8001, True),  # Over limit
        ("amazon.titan-text-lite-v1", 4000, False),  # At limit
        ("amazon.titan-text-lite-v1", 4001, True),  # Over limit
        ("amazon.titan-text-premier-v1:0", 3072, False),  # At limit
        ("amazon.titan-text-premier-v1:0", 3073, True),  # Over limit
        ("amazon.titan-text-express-v1", 0, True),  # Zero tokens
        ("amazon.titan-text-express-v1", -1, True),  # Negative tokens
    ],
)
def test_token_limits(model_id: str, max_tokens: int, should_raise: bool):
    """Test token limit validation for different models."""
    model = TitanModel(model_id)
    model.set_config(
        {
            "max_tokens": max_tokens,
            "default_tokens": 2048,
        }
    )

    if should_raise:
        with pytest.raises(ValueError, match="exceeds model's limit"):
            model.format_request("test", max_tokens=max_tokens + 1)
    else:
        request = model.format_request("test", max_tokens=max_tokens)
        assert request["textGenerationConfig"]["maxTokenCount"] == max_tokens


def test_default_token_count():
    """Test default token count is used when max_tokens is not specified."""
    model = TitanModel("amazon.titan-text-express-v1")
    model.set_config(
        {
            "max_tokens": 8000,
            "default_tokens": 2048,
        }
    )
    request = model.format_request("test")
    assert request["textGenerationConfig"]["maxTokenCount"] == 2048


@pytest.fixture
def model() -> TitanModel:
    """Create a Titan model instance."""
    model = TitanModel("amazon.titan-text-express-v1")
    model.set_config(
        {
            "max_tokens": 8000,
            "default_tokens": 2048,
        }
    )
    return model


@pytest.fixture
def mock_client() -> MagicMock:
    """Create a mock Bedrock client."""
    return MagicMock()


def test_format_request(model: TitanModel) -> None:
    """Test request formatting."""
    # Basic request
    request = model.format_request(message="Test message")
    assert request == {
        "inputText": "Test message",
        "textGenerationConfig": {
            "temperature": 0.7,
            "topP": 1,
            "maxTokenCount": 2048,
            "stopSequences": [],
        },
    }

    # Request with system prompt and custom parameters
    request = model.format_request(
        message="Test message",
        system="Test system",
        temperature=0.5,
        max_tokens=100,
    )
    assert request == {
        "inputText": "Test system\n\nTest message",
        "textGenerationConfig": {
            "temperature": 0.5,
            "topP": 1,
            "maxTokenCount": 100,
            "stopSequences": [],
        },
    }

    # Test empty system prompt
    request = model.format_request(message="Test message", system="")
    assert request["inputText"] == "Test message"

    # Test temperature validation
    with pytest.raises(ValueError, match="Temperature must be between 0.0 and 1.0"):
        model.format_request(message="Test", temperature=-0.1)
    with pytest.raises(ValueError, match="Temperature must be between 0.0 and 1.0"):
        model.format_request(message="Test", temperature=1.1)


def test_process_response(model: TitanModel) -> None:
    """Test response processing."""
    # Test successful response processing
    mock_response = {
        "body": [
            {"chunk": {"bytes": json.dumps({"outputText": "Hello"}).encode()}},
            {"chunk": {"bytes": json.dumps({"outputText": " world"}).encode()}},
        ]
    }
    result = model.process_response(mock_response)
    assert result == {"type": "message", "content": "Hello world"}

    # Test invalid JSON
    mock_response = {"body": [{"chunk": {"bytes": b"invalid json"}}]}
    result = model.process_response(mock_response)
    assert result == {"type": "message", "content": ""}

    # Test missing required fields
    mock_response = {
        "body": [{"chunk": {"bytes": json.dumps({"wrong_field": "value"}).encode()}}]
    }
    result = model.process_response(mock_response)
    assert result == {"type": "message", "content": ""}

    # Test empty response
    mock_response = {"body": []}
    result = model.process_response(mock_response)
    assert result == {"type": "message", "content": ""}

    # Test missing chunk key
    mock_response = {"body": [{"not_chunk": {"bytes": b"{}"}}]}
    result = model.process_response(mock_response)
    assert result == {"type": "message", "content": ""}

    # Test missing bytes key
    mock_response = {"body": [{"chunk": {"not_bytes": b"{}"}}]}
    result = model.process_response(mock_response)
    assert result == {"type": "message", "content": ""}

    # Test whitespace handling
    mock_response = {
        "body": [
            {"chunk": {"bytes": json.dumps({"outputText": "  Hello  "}).encode()}},
            {"chunk": {"bytes": json.dumps({"outputText": "  world  "}).encode()}},
        ]
    }
    result = model.process_response(mock_response)
    assert result == {"type": "message", "content": "Hello world"}

    # Test invalid chunk format
    mock_response = {"body": [{"chunk": None}]}
    result = model.process_response(mock_response)
    assert result == {"type": "message", "content": ""}


def test_invoke(model: TitanModel, mock_client: MagicMock) -> None:
    """Test model invocation."""
    # Test successful invocation
    mock_response = {
        "body": [
            {"chunk": {"bytes": json.dumps({"outputText": "Test response"}).encode()}}
        ]
    }
    mock_client.invoke_model_with_response_stream.return_value = mock_response

    response = model._invoke_with_retry(
        client=mock_client,
        request={
            "inputText": "Test message",
            "textGenerationConfig": {
                "temperature": 0.5,
                "topP": 1,
                "maxTokenCount": 100,
                "stopSequences": [],
            },
        },
    )
    assert response == mock_response

    # Verify request format
    mock_client.invoke_model_with_response_stream.assert_called_once()
    call_args = mock_client.invoke_model_with_response_stream.call_args[1]
    assert call_args["modelId"] == model.get_model_id()
    request_body = json.loads(call_args["body"])
    assert request_body["inputText"] == "Test message"
    assert request_body["textGenerationConfig"]["temperature"] == 0.5
    assert request_body["textGenerationConfig"]["maxTokenCount"] == 100

    # Test client error
    error_response = {"Error": {"Code": "ServiceError", "Message": "API error"}}
    mock_client.invoke_model_with_response_stream.side_effect = ClientError(
        error_response, "invoke_model_with_response_stream"
    )
    with pytest.raises(ModelInvokeError, match="Error invoking model"):
        model._invoke_with_retry(client=mock_client, request={})


def test_invoke_with_retry(model: TitanModel, mock_client: MagicMock) -> None:
    """Test retry behavior in model invocation."""
    # Mock time.sleep to avoid actual delays
    with patch("time.sleep"):
        # Test throttling with successful retry
        error_response = {
            "Error": {"Code": "ThrottlingException", "Message": "Rate exceeded"}
        }
        mock_client.invoke_model_with_response_stream.side_effect = [
            ClientError(error_response, "invoke_model_with_response_stream"),
            {
                "body": [
                    {"chunk": {"bytes": json.dumps({"outputText": "Success"}).encode()}}
                ]
            },
        ]

        response = model._invoke_with_retry(
            client=mock_client,
            request={
                "inputText": "Test message",
                "textGenerationConfig": {
                    "temperature": 0.7,
                    "topP": 1,
                    "maxTokenCount": 2048,
                    "stopSequences": [],
                },
            },
        )
        assert "body" in response
        assert mock_client.invoke_model_with_response_stream.call_count == 2

        # Test max retries exceeded
        mock_client.invoke_model_with_response_stream.reset_mock()
        mock_client.invoke_model_with_response_stream.side_effect = ClientError(
            error_response, "invoke_model_with_response_stream"
        )
        with pytest.raises(ModelInvokeError, match="Error invoking model"):
            model._invoke_with_retry(client=mock_client, request={})


def test_extract_content_error_handling(model: TitanModel) -> None:
    """Test error handling in content extraction."""
    # Test JSON decode error
    mock_response = {"body": [{"chunk": {"bytes": b"invalid json"}}]}
    result = model.process_response(mock_response)
    assert result == {"type": "message", "content": ""}

    # Test missing chunk
    mock_response = {"body": [{"not_chunk": {}}]}
    result = model.process_response(mock_response)
    assert result == {"type": "message", "content": ""}

    # Test missing bytes
    mock_response = {"body": [{"chunk": {"not_bytes": {}}}]}
    result = model.process_response(mock_response)
    assert result == {"type": "message", "content": ""}

    # Test invalid chunk type
    mock_response = {"body": [{"chunk": None}]}
    result = model.process_response(mock_response)
    assert result == {"type": "message", "content": ""}
