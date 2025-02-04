from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseTool(ABC):
    """Base class for tools that can be used by agents.
    
    All tools must implement:
    - name: Tool name
    - description: Tool description
    - get_schema: Method to get JSON schema
    - execute: Method to execute the tool
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Get tool name."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Get tool description."""
        pass
    
    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """Get JSON schema for the tool.
        
        Returns:
            Dict[str, Any]: Tool schema
        """
        pass
    
    @abstractmethod
    async def execute(self, **kwargs: Any) -> str:
        """Execute the tool with given parameters.
        
        Args:
            **kwargs: Tool parameters
            
        Returns:
            str: Tool execution result
        """
        pass 