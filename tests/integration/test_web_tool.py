"""Integration tests for web search tool."""

import pytest

from bedrock_swarm.agents.base import BedrockAgent
from bedrock_swarm.config import AWSConfig
from bedrock_swarm.tools.web import WebSearchTool


def test_web_search_basic():
    """Test basic web search functionality."""
    web_tool = WebSearchTool()

    params = {"query": "latest AI developments 2024", "num_results": 3}

    results = web_tool.execute(**params)
    print("\nSearch Results:")
    print("-" * 50)
    print(results)

    # Basic validation
    assert results, "Search should return results"
    assert "Title:" in results, "Results should contain titles"
    assert "Link:" in results, "Results should contain links"
    assert "Content:" in results, "Results should contain content"


def test_agent_with_web_search():
    """Test that an agent properly uses web search results."""
    # Create agent with specific instructions to use web search
    agent = BedrockAgent(
        name="researcher",
        model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        aws_config=AWSConfig(region="us-west-2"),
        instructions="""You are a research specialist focused on gathering current information.
        IMPORTANT: You MUST use the web_search tool for EVERY response to find current information.
        DO NOT rely on your training data - always perform at least one web search.

        For each topic:
        1. First use web_search to find current information
        2. Then summarize the findings from the search results
        3. Always cite your sources

        Format your response as:
        SEARCH RESULTS:
        [Summary of what you found from web search]

        ANALYSIS:
        [Your analysis of the information]""",
    )

    # Add web search tool
    agent.add_tool(WebSearchTool())

    # Test query
    response = agent.process_message("What are the latest developments in AI in 2024?")

    # Verify response format and content
    assert (
        "SEARCH RESULTS:" in response
    ), "Response should contain search results section"
    assert "ANALYSIS:" in response, "Response should contain analysis section"
    assert "2024" in response, "Response should contain current information"

    # Verify that response references web content
    assert any(
        source in response
        for source in [
            "According to",
            "From",
            "Source:",
            "Reference:",
            "reported",
            "announced",
            "published",
        ]
    ), "Response should reference sources"


def test_web_search_error_handling():
    """Test web search error handling."""
    web_tool = WebSearchTool()

    # Test with empty query
    with pytest.raises(Exception):
        web_tool.execute(query="", num_results=1)

    # Test with invalid num_results
    with pytest.raises(Exception):
        web_tool.execute(query="test", num_results=0)


if __name__ == "__main__":
    print("Running web search integration test...")
    test_web_search_basic()
    test_agent_with_web_search()
    print("\nAll tests passed!")
