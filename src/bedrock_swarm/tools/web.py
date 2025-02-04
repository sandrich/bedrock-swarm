from typing import Any, Dict
from duckduckgo_search import DDGS

from .base import BaseTool

class WebSearchTool(BaseTool):
    """Tool for performing web searches using DuckDuckGo.
    
    This tool uses the DuckDuckGo API to perform searches,
    providing reliable and efficient access to web search results.
    """
    
    def __init__(self):
        self._ddgs = DDGS()
    
    @property
    def name(self) -> str:
        return "web_search"
    
    @property
    def description(self) -> str:
        return "Search the web for information on a given query using DuckDuckGo"
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    },
                    "num_results": {
                        "type": "integer",
                        "description": "Number of results to return",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        }
    
    async def execute(self, query: str, num_results: int = 5) -> str:
        """Execute web search using DuckDuckGo.
        
        Args:
            query (str): Search query
            num_results (int): Number of results to return
            
        Returns:
            str: Search results formatted as a string
        """
        try:
            # Perform the search
            results = list(self._ddgs.text(
                query,
                max_results=num_results
            ))
            
            if not results:
                return "No results found"
            
            # Format results
            formatted_results = []
            for i, result in enumerate(results, 1):
                title = result.get('title', 'No title')
                link = result.get('link', 'No link')
                snippet = result.get('body', 'No description available')
                formatted_results.append(f"{i}. {title}\n   {link}\n   {snippet}\n")
            
            return "\n".join(formatted_results)
            
        except Exception as e:
            return f"Error during search: {str(e)}" 