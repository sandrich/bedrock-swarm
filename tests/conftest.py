"""Shared test fixtures for bedrock-swarm tests."""

from typing import Any, Dict, Generator, List, Optional, cast
from unittest.mock import MagicMock, patch

import pytest

from bedrock_swarm.config import AWSConfig
from bedrock_swarm.models.base import BedrockModel
from bedrock_swarm.tools.base import BaseTool


@pytest.fixture(autouse=True)
def mock_aws_session() -> Generator[MagicMock, None, None]:
    """Mock AWS session for all tests."""
    with patch("boto3.Session") as mock_session:
        session = MagicMock()
        mock_client = MagicMock()

        # Set up standard response for non-streaming calls
        mock_response = {
            "completion": "Test response",
            "stop_reason": "stop",
        }
        mock_body = MagicMock()
        mock_body.read = MagicMock(return_value=mock_response)
        mock_client.invoke_model = MagicMock(return_value={"body": mock_body})

        # Set up streaming response
        mock_stream = MagicMock()
        mock_stream.__iter__ = MagicMock(
            return_value=iter(
                [
                    {
                        "chunk": {
                            "bytes": b'{"type": "content_block_delta", "delta": {"text": "Test streaming response"}}'
                        }
                    }
                ]
            )
        )
        mock_stream.close = MagicMock()
        mock_client.invoke_model_with_response_stream = MagicMock(
            return_value={"body": mock_stream}
        )

        session.client.return_value = mock_client
        mock_session.return_value = session
        yield mock_session


# AWS Configuration Fixtures
@pytest.fixture
def aws_config() -> AWSConfig:
    """Fixture providing a standard AWS configuration for testing."""
    return AWSConfig(
        region="us-west-2",
        profile="default",
        endpoint_url="https://bedrock-runtime.us-west-2.amazonaws.com",
    )


# Mock AWS Fixtures
@pytest.fixture
def mock_boto3_session() -> Generator[MagicMock, None, None]:
    """Fixture providing a mocked boto3 Session."""
    with patch("boto3.Session") as mock_session:
        mock_client = MagicMock()
        mock_session.return_value.client.return_value = mock_client
        yield mock_session


@pytest.fixture
def mock_boto3_client() -> Generator[MagicMock, None, None]:
    """Fixture providing a mocked boto3 client."""
    with patch("boto3.client") as mock_client:
        yield mock_client


# Mock Tool Fixtures
class MockTool(BaseTool):
    """Mock tool implementation for testing."""

    def __init__(self, name: str = "mock_tool", should_fail: bool = False) -> None:
        """Initialize the mock tool.

        Args:
            name: Name of the tool
            should_fail: Whether the tool should fail on execution
        """
        self._name = name
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

    def get_schema(self) -> Dict[str, Any]:
        """Get tool schema."""
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

    def _execute_impl(self, **kwargs: Any) -> str:
        """Execute the mock tool."""
        if self.should_fail:
            raise Exception("Tool execution failed")
        return f"Executed with params: {kwargs}"


@pytest.fixture
def mock_tool() -> MockTool:
    """Fixture providing a mock tool instance."""
    return MockTool()


# Mock Model Fixtures
class MockBedrockModel(BedrockModel):
    """Mock model implementation for testing."""

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
        max_tokens: Optional[int] = None,
        tool_map: Optional[Dict[str, BaseTool]] = None,
    ) -> str:
        """Process a message."""
        return "Mock response"

    def format_request(
        self,
        message: str,
        system: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> Dict[str, Any]:
        """Format a request."""
        return {"mock": "request"}

    def parse_response(self, response: Dict[str, Any]) -> str:
        """Parse a response."""
        return cast(str, response.get("response", ""))

    def parse_stream_chunk(self, chunk: Dict[str, Any]) -> Optional[str]:
        """Parse a stream chunk."""
        return cast(str, chunk.get("chunk", ""))


@pytest.fixture
def mock_model() -> MockBedrockModel:
    """Fixture providing a mock model instance."""
    return MockBedrockModel()


# Web Request Fixtures
@pytest.fixture
def mock_requests() -> Generator[MagicMock, None, None]:
    """Fixture providing mocked requests library."""
    with patch("requests.get") as mock_get:
        yield mock_get


@pytest.fixture
def mock_beautifulsoup() -> Generator[MagicMock, None, None]:
    """Fixture providing mocked BeautifulSoup."""
    with patch("bs4.BeautifulSoup") as mock_bs:
        yield mock_bs
