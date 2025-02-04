import json
import pytest
from unittest.mock import Mock, patch

from bedrock_swarm.tools.web import WebSearchTool
from bedrock_swarm.tools.factory import ToolFactory

@pytest.fixture(autouse=True)
def clear_tool_registry():
    """Clear tool registry before each test."""
    ToolFactory.clear()
    yield
    ToolFactory.clear()

@pytest.fixture
def web_search_tool():
    return WebSearchTool()

@pytest.fixture
def mock_search_results():
    return [
        {
            'title': 'First Result Title',
            'link': 'https://example.com/1',
            'body': 'First result description'
        },
        {
            'title': 'Second Test Result',
            'link': 'https://example.com/2',
            'body': 'Second result with special chars'
        }
    ]

@pytest.mark.asyncio
async def test_web_search_basic(web_search_tool, mock_search_results):
    """Test basic web search functionality."""
    with patch("duckduckgo_search.DDGS.text") as mock_search:
        mock_search.return_value = mock_search_results

        result = await web_search_tool.execute("test query", num_results=2)

        # Verify the search call
        mock_search.assert_called_once_with("test query", max_results=2)

        # Verify the results
        assert "First Result Title" in result
        assert "https://example.com/1" in result
        assert "First result description" in result
        assert "Second Test Result" in result
        assert "https://example.com/2" in result
        assert "Second result with special chars" in result

@pytest.mark.asyncio
async def test_web_search_no_results(web_search_tool):
    """Test web search with no results."""
    with patch("duckduckgo_search.DDGS.text") as mock_search:
        mock_search.return_value = []

        result = await web_search_tool.execute("nonexistent query")
        assert result == "No results found"

@pytest.mark.asyncio
async def test_web_search_error(web_search_tool):
    """Test web search with error."""
    with patch("duckduckgo_search.DDGS.text") as mock_search:
        mock_search.side_effect = Exception("Search error")

        result = await web_search_tool.execute("test query")
        assert "Error during search: Search error" in result

def test_web_search_schema(web_search_tool):
    """Test web search tool schema."""
    schema = web_search_tool.get_schema()
    
    assert schema["name"] == "web_search"
    assert "DuckDuckGo" in schema["description"]
    assert schema["parameters"]["properties"]["query"]["type"] == "string"
    assert schema["parameters"]["properties"]["num_results"]["type"] == "integer"
    assert schema["parameters"]["properties"]["num_results"]["default"] == 5
    assert schema["parameters"]["required"] == ["query"]

@pytest.mark.asyncio
async def test_web_search_partial_results(web_search_tool):
    """Test web search with partial/malformed results."""
    malformed_results = [
        {
            'title': 'Good Result',
            'link': 'https://example.com/1',
            'body': 'Good description'
        },
        {
            # Missing link and body
            'title': 'Missing Fields'
        }
    ]
    
    with patch("duckduckgo_search.DDGS.text") as mock_search:
        mock_search.return_value = malformed_results

        result = await web_search_tool.execute("test query", num_results=2)
        
        # Should still get the good result
        assert "Good Result" in result
        assert "https://example.com/1" in result
        assert "Good description" in result
        # Should handle missing fields gracefully
        assert "Missing Fields" in result
        assert "No link" in result
        assert "No description available" in result 