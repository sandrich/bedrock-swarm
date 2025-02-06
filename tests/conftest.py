"""Shared test fixtures for bedrock-swarm tests."""

from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pytest

from bedrock_swarm.config import AWSConfig
from bedrock_swarm.models.base import BedrockModel
from bedrock_swarm.tools.base import BaseTool


# AWS Configuration Fixtures
@pytest.fixture
def aws_config():
    """Fixture providing a standard AWS configuration for testing."""
    return AWSConfig(
        region="us-west-2",
        profile="default",
        endpoint_url="https://bedrock-runtime.us-west-2.amazonaws.com",
    )


# Mock AWS Fixtures
@pytest.fixture
def mock_boto3_session():
    """Fixture providing a mocked boto3 Session."""
    with patch("boto3.Session") as mock_session:
        mock_client = MagicMock()
        mock_session.return_value.client.return_value = mock_client
        yield mock_session


@pytest.fixture
def mock_boto3_client():
    """Fixture providing a mocked boto3 client."""
    with patch("boto3.client") as mock_client:
        yield mock_client


# Mock Tool Fixtures
class MockTool(BaseTool):
    """Mock tool implementation for testing."""

    def __init__(self, name="mock_tool", should_fail=False):
        self.name = name
        self.should_fail = should_fail

    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": "Mock tool for testing",
            "parameters": {
                "properties": {
                    "param1": {"description": "Test parameter"},
                    "param2": {"description": "Optional parameter"},
                },
                "required": ["param1"],
            },
        }

    def execute(self, **kwargs) -> str:
        if self.should_fail:
            raise Exception("Tool execution failed")
        return f"Executed with params: {kwargs}"


@pytest.fixture
def mock_tool():
    """Fixture providing a mock tool instance."""
    return MockTool()


# Mock Model Fixtures
class MockBedrockModel(BedrockModel):
    """Mock model implementation for testing."""

    def get_default_max_tokens(self) -> int:
        return 4096

    def supports_tools(self) -> bool:
        return True

    def supports_streaming(self) -> bool:
        return True

    def process_message(self, *args, **kwargs) -> str:
        return "Mock response"

    def format_request(self, *args, **kwargs) -> Dict[str, Any]:
        return {"mock": "request"}

    def parse_response(self, response: Dict[str, Any]) -> str:
        return response.get("response", "")

    def parse_stream_chunk(self, chunk: Dict[str, Any]) -> str:
        return chunk.get("chunk", "")


@pytest.fixture
def mock_model():
    """Fixture providing a mock model instance."""
    return MockBedrockModel()


# Web Request Fixtures
@pytest.fixture
def mock_requests():
    """Fixture providing mocked requests library."""
    with patch("requests.get") as mock_get:
        yield mock_get


@pytest.fixture
def mock_beautifulsoup():
    """Fixture providing mocked BeautifulSoup."""
    with patch("bs4.BeautifulSoup") as mock_bs:
        yield mock_bs
