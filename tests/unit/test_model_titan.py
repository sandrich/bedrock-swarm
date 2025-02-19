"""Tests for Titan model implementation."""

import json
from unittest.mock import MagicMock

import pytest

from bedrock_swarm.exceptions import ModelInvokeError, ResponseParsingError
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
    with pytest.raises(ResponseParsingError, match="Error parsing chunk"):
        model.process_response(mock_response)

    # Test missing required fields
    mock_response = {
        "body": [{"chunk": {"bytes": json.dumps({"wrong_field": "value"}).encode()}}]
    }
    result = model.process_response(mock_response)
    assert result == {"type": "message", "content": ""}
