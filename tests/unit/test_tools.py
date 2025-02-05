"""Tests for the tools functionality."""

# mypy: ignore-errors

from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pytest

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
def mock_search_results() -> Dict[str, Any]:
    """Create mock search results for testing."""
    return [
        {
            "title": "Test Result 1",
            "link": "https://example.com/1",
            "body": "This is test result 1",
        },
        {
            "title": "Test Result 2",
            "link": "https://example.com/2",
            "body": "This is test result 2",
        },
    ]


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

    def execute(self, **kwargs: Any) -> str:
        """Execute the tool."""
        return self._execute_mock(**kwargs)


def test_web_search_basic(
    web_search_tool: WebSearchTool, mock_search_results: Dict[str, Any]
) -> None:
    """Test basic web search functionality."""
    with patch("duckduckgo_search.DDGS") as mock_ddgs:
        mock_instance = MagicMock()
        mock_instance.text.return_value = mock_search_results
        mock_ddgs.return_value = mock_instance

        result = web_search_tool.execute(query="test query")
        assert "Test Result 1" in result
        assert "Test Result 2" in result
        assert "https://example.com/1" in result
        assert "https://example.com/2" in result
        assert "This is test result 1" in result
        assert "This is test result 2" in result


def test_web_search_no_results(web_search_tool: WebSearchTool) -> None:
    """Test web search with no results."""
    with patch("duckduckgo_search.DDGS") as mock_ddgs:
        mock_instance = MagicMock()
        mock_instance.text.return_value = []
        mock_ddgs.return_value = mock_instance

        result = web_search_tool.execute(query="test query")
        assert "No results found" in result


def test_web_search_error(web_search_tool: WebSearchTool) -> None:
    """Test web search error handling."""
    with patch("duckduckgo_search.DDGS") as mock_ddgs:
        mock_instance = MagicMock()
        mock_instance.text.side_effect = Exception("Search failed")
        mock_ddgs.return_value = mock_instance

        result = web_search_tool.execute(query="test query")
        assert "Error during search: Search failed" in result


def test_web_search_partial_results(web_search_tool: WebSearchTool) -> None:
    """Test web search with partial results."""
    with patch("duckduckgo_search.DDGS") as mock_ddgs:
        mock_instance = MagicMock()
        mock_instance.text.return_value = [
            {
                "title": "Partial Result",
                # Missing 'link' field
                "body": "This is a partial result",
            }
        ]
        mock_ddgs.return_value = mock_instance

        result = web_search_tool.execute(query="test query")
        assert "Partial Result" in result
        assert "This is a partial result" in result


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
    assert isinstance(tool.get_schema(), dict)


def test_web_search_execution():
    """Test web search execution."""
    with patch("duckduckgo_search.DDGS") as mock_ddgs:
        mock_instance = MagicMock()
        mock_instance.text.return_value = [
            {
                "title": "Test Result",
                "link": "https://test.com",
                "body": "Test body",
            }
        ]
        mock_ddgs.return_value = mock_instance

        tool = WebSearchTool()
        result = tool.execute(query="test query", num_results=1)

        assert "Test Result" in result
        assert "https://test.com" in result
        assert "Test body" in result
        mock_instance.text.assert_called_once_with("test query", max_results=1)
