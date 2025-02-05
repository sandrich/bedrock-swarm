"""Web search tool."""

from typing import Any, Dict, List

from duckduckgo_search import DDGS

from .base import BaseTool


class WebSearchTool(BaseTool):
    """Tool for performing web searches using DuckDuckGo."""

    def __init__(
        self,
        name: str = "web_search",
        description: str = "Search the web for information",
    ) -> None:
        """Initialize the web search tool."""
        super().__init__(name=name, description=description)
        self.ddgs = DDGS()

    @property
    def name(self) -> str:
        """Get tool name."""
        return "web_search"

    @property
    def description(self) -> str:
        """Get tool description."""
        return "Search the web for information using DuckDuckGo"

    def get_schema(self) -> Dict[str, Any]:
        """Get JSON schema for the tool.

        Returns:
            Dict[str, Any]: Tool schema
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "num_results": {
                        "type": "integer",
                        "description": "Number of results to return",
                        "default": 5,
                        "minimum": 1,
                        "maximum": 10,
                    },
                },
                "required": ["query"],
            },
        }

    def _execute_impl(self, **kwargs: Any) -> str:
        """Execute the web search.

        Args:
            **kwargs: Tool parameters

        Returns:
            str: Search results
        """
        query = kwargs["query"]
        num_results = kwargs.get("num_results", 5)

        try:
            results = list(self.ddgs.text(query, max_results=num_results))
            return self._format_results(results)
        except Exception as e:
            return f"Error during search: {str(e)}"

    def _format_results(self, results: List[Dict[str, str]]) -> str:
        """Format search results.

        Args:
            results: List of search results

        Returns:
            str: Formatted results
        """
        if not results:
            return "No results found"

        formatted = []
        for result in results:
            title = result.get("title", "No title")
            link = result.get("link", "No link")
            body = result.get("body", "No description available")

            formatted.append(f"Title: {title}")
            formatted.append(f"Link: {link}")
            formatted.append(f"Description: {body}")
            formatted.append("")

        return "\n".join(formatted)
