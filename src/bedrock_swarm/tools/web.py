"""Web search tool."""

from typing import Any, Dict

import requests
from bs4 import BeautifulSoup
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

    def _fetch_page_content(self, url: str) -> str:
        """Fetch webpage content with minimal cleaning.

        Only performs basic text extraction and error handling.
        Content filtering and analysis should be done by the consumer.
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # Get body or fall back to full document
            content = soup.find("body") or soup

            # Basic text extraction with minimal cleaning
            text = content.get_text(separator="\n", strip=True)

            # Only truncate if extremely long to prevent memory issues
            # Let the consumer handle more specific truncation
            if (
                len(text) > 10000
            ):  # Allow more content, let consumer decide how much they want
                return text[:10000] + "... (content truncated)"

            return text

        except requests.exceptions.RequestException as e:
            print(f"Error fetching content from {url}: {str(e)}")
            return f"Error fetching content: {str(e)}"

    def _execute_impl(self, **kwargs: Any) -> str:
        """Execute the web search."""
        query = kwargs["query"]
        num_results = kwargs.get("num_results", 3)

        try:
            results = self.ddgs.text(query, max_results=num_results)

            print("\nRaw search results:")
            for r in results:
                print(f"Raw result: {r}")

            formatted_results = ["Search Results:", "-" * 50]  # Single header

            for result in results:
                title = result.get("title", "No title")
                link = result.get("href", "No link")
                summary = result.get("body", "No summary available")

                formatted_results.extend(
                    [
                        f"Title: {title}",
                        f"Link: {link}",
                        "Content:",
                        f"Summary: {summary}\n",
                    ]
                )

                if link != "No link":
                    full_content = self._fetch_page_content(link)
                    if (
                        full_content
                        and full_content != "Could not fetch content"
                        and full_content != "Could not find page content"
                    ):
                        formatted_results.extend(["Full content:", full_content])

                formatted_results.append("-" * 50)

            return "\n".join(formatted_results)

        except Exception as e:
            print(f"Search error: {str(e)}")
            return f"Error performing web search: {str(e)}"
