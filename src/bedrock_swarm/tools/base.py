"""Module for defining base tool functionality."""

from abc import ABC, abstractmethod
from typing import Any, Dict

from ..exceptions import ToolError
from .validation import validate_tool_parameters, validate_tool_schema


class BaseTool(ABC):
    """Base class for tools that can be used by agents.

    All tools must implement:
    - name: Tool name
    - description: Tool description
    - get_schema: Method to get JSON schema
    - execute: Method to execute the tool
    """

    def __init__(self, name: str, description: str) -> None:
        """Initialize the tool and validate schema.

        Args:
            name (str): Tool name
            description (str): Tool description
        """
        self._name = name
        self._description = description
        schema = self.get_schema()
        validate_tool_schema(self.name, schema)

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

    def execute(self, **kwargs: Any) -> str:
        """Execute the tool with given parameters.

        Args:
            **kwargs: Tool parameters

        Returns:
            str: Tool execution result

        Raises:
            ToolError: If tool execution fails
        """
        try:
            validate_tool_parameters(self.get_schema(), **kwargs)
            return self._execute_impl(**kwargs)
        except Exception as e:
            if isinstance(e, ToolError):
                raise
            raise ToolError(str(e))

    @abstractmethod
    def _execute_impl(self, **kwargs: Any) -> str:
        """Execute the tool implementation.

        This method should be implemented by subclasses to provide the actual
        tool functionality. The base class handles parameter validation.

        Args:
            **kwargs: Tool parameters

        Returns:
            str: Tool execution result

        Raises:
            ToolError: If tool execution fails
        """
        pass
