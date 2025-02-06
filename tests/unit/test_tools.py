"""Tests for the tools functionality."""

# mypy: ignore-errors

from typing import Any, Dict
from unittest import mock
from unittest.mock import MagicMock, patch

import pytest
import requests

from bedrock_swarm.tools.base import BaseTool
from bedrock_swarm.tools.web import WebSearchTool


@pytest.fixture
def clear_tool_registry() -> None:
    """Clear the tool registry before and after each test."""
    BaseTool._registry = {}  # type: ignore
    yield
    BaseTool._registry = {}  # type: ignore


@pytest.fixture
def web_search_tool() -> WebSearchTool:
    """Create a WebSearchTool instance for testing."""
    return WebSearchTool(name="web_search", description="Search the web")


@pytest.fixture
def mock_search_results() -> list[Dict[str, Any]]:
    """Create mock search results for testing."""
    return [
        {
            "title": "Test Result 1",
            "href": "https://example.com/1",
            "body": "This is test result 1",
        },
        {
            "title": "Test Result 2",
            "href": "https://example.com/2",
            "body": "This is test result 2",
        },
    ]


@pytest.fixture
def mock_page_content() -> str:
    """Create mock webpage content for testing."""
    return """
    <html>
        <body>
            <h1>Test Page</h1>
            <p>This is the full content of the test page.</p>
            <p>It contains multiple paragraphs of information.</p>
        </body>
    </html>
    """


class MockTool(BaseTool):
    """Mock tool for testing."""

    def __init__(self, name: str, description: str) -> None:
        """Initialize the mock tool."""
        super().__init__(name=name, description=description)
        self._execute_mock = MagicMock(return_value="Mock result")

    @property
    def name(self) -> str:
        """Get tool name."""
        return self._name

    @property
    def description(self) -> str:
        """Get tool description."""
        return self._description

    def get_schema(self) -> Dict[str, Any]:
        """Get the schema for the mock tool."""
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


def test_web_search_basic(
    web_search_tool: WebSearchTool,
    mock_search_results: list[Dict[str, Any]],
    mock_page_content: str,
) -> None:
    """Test basic web search functionality with content fetching."""
    with (
        patch.object(web_search_tool.ddgs, "text") as mock_text,
        patch("requests.get") as mock_get,
    ):
        # Mock search results
        mock_text.return_value = mock_search_results

        # Mock webpage content fetching
        mock_response = MagicMock()
        mock_response.text = mock_page_content
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = web_search_tool.execute(query="test query")

        # Verify search results
        assert "Test Result 1" in result
        assert "Test Result 2" in result
        assert "https://example.com/1" in result
        assert "https://example.com/2" in result
        assert "This is test result 1" in result
        assert "This is test result 2" in result

        # Verify content fetching
        assert "Test Page" in result
        assert "This is the full content" in result
        assert "multiple paragraphs" in result

        # Verify proper headers were used for all URLs
        expected_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }

        # Check that both URLs were fetched with correct headers
        assert mock_get.call_count == 2
        mock_get.assert_has_calls(
            [
                mock.call(
                    "https://example.com/1", headers=expected_headers, timeout=10
                ),
                mock.call(
                    "https://example.com/2", headers=expected_headers, timeout=10
                ),
            ],
            any_order=True,
        )


def test_web_search_no_results(web_search_tool: WebSearchTool) -> None:
    """Test web search with no results."""
    with patch.object(web_search_tool.ddgs, "text") as mock_text:
        mock_text.return_value = []
        result = web_search_tool.execute(query="test query")
        assert "Search Results:" in result
        assert "-" * 50 in result


def test_web_search_error(web_search_tool: WebSearchTool) -> None:
    """Test web search error handling."""
    with patch.object(web_search_tool.ddgs, "text") as mock_text:
        mock_text.side_effect = Exception("Search failed")
        result = web_search_tool.execute(query="test query")
        assert "Error performing web search: Search failed" in result


def test_web_search_content_fetch_error(
    web_search_tool: WebSearchTool, mock_search_results: list[Dict[str, Any]]
) -> None:
    """Test error handling during content fetching."""
    with (
        patch.object(web_search_tool.ddgs, "text") as mock_text,
        patch("requests.get") as mock_get,
    ):
        # Mock search results
        mock_text.return_value = mock_search_results

        # Mock content fetch error
        mock_get.side_effect = requests.RequestException("Failed to fetch content")

        result = web_search_tool.execute(query="test query")

        # Should still show search results
        assert "Test Result 1" in result
        assert "This is test result 1" in result
        # Should show error for content fetch
        assert "Error fetching content" in result


def test_web_search_content_truncation(
    web_search_tool: WebSearchTool, mock_search_results: list[Dict[str, Any]]
) -> None:
    """Test content truncation for long pages."""
    with (
        patch.object(web_search_tool.ddgs, "text") as mock_text,
        patch("requests.get") as mock_get,
    ):
        # Mock search results
        mock_text.return_value = mock_search_results

        # Create very long content
        long_content = "<html><body>" + ("x" * 15000) + "</body></html>"

        # Mock webpage content fetching
        mock_response = MagicMock()
        mock_response.text = long_content
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = web_search_tool.execute(query="test query")

        # Verify content was truncated
        assert "content truncated" in result
        # The result includes headers and formatting, so we just check it's shorter than input
        assert len(result.strip()) < len(long_content) * 2


def test_base_tool():
    """Test base tool functionality."""
    tool = MockTool(name="mock_tool", description="Mock tool")
    assert tool.name == "mock_tool"
    assert isinstance(tool.get_schema(), dict)


def test_tool_execution():
    """Test tool execution."""
    tool = MockTool(name="mock_tool", description="Mock tool")
    result = tool.execute(param1="test", param2=123)
    assert result == "Mock result"
    tool._execute_mock.assert_called_once_with(param1="test", param2=123)


def test_web_search_tool():
    """Test web search tool."""
    tool = WebSearchTool()
    assert tool.name == "web_search"
    schema = tool.get_schema()
    assert isinstance(schema, dict)
    assert "query" in schema["parameters"]["properties"]
    assert "num_results" in schema["parameters"]["properties"]
    assert schema["parameters"]["required"] == ["query"]


def test_web_search_invalid_params(web_search_tool: WebSearchTool):
    """Test web search with invalid parameters."""
    # Test with empty query
    result = web_search_tool.execute(query="")
    assert "Error performing web search: keywords is mandatory" in result

    # Test with invalid num_results
    with pytest.raises(ValueError, match="Invalid parameter type"):
        web_search_tool.execute(query="test", num_results=0)

    with pytest.raises(ValueError, match="Invalid parameter type"):
        web_search_tool.execute(query="test", num_results=11)  # Exceeds maximum
