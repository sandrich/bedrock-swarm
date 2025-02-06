"""Tool factory for creating tool instances."""

from typing import Dict, Type

from ..exceptions import ToolError
from .base import BaseTool
from .time import CurrentTimeTool


class ToolFactory:
    """Factory for creating tool instances."""

    _tool_types: Dict[str, Type[BaseTool]] = {}

    @classmethod
    def register_tool_type(cls, tool_type: Type[BaseTool]) -> None:
        """Register a tool type.

        Args:
            tool_type: Tool class to register

        Raises:
            ToolError: If tool type is already registered
        """
        name = tool_type.__name__
        if name in cls._tool_types:
            raise ToolError(f"Tool type {name} already registered")
        cls._tool_types[name] = tool_type

    @classmethod
    def create_tool(cls, tool_type: str, **kwargs: str) -> BaseTool:
        """Create a tool instance.

        Args:
            tool_type: Name of tool type to create
            **kwargs: Arguments to pass to tool constructor

        Returns:
            Created tool instance

        Raises:
            ToolError: If tool type is not registered
        """
        if tool_type not in cls._tool_types:
            raise ToolError(f"Tool type {tool_type} not registered")
        return cls._tool_types[tool_type](**kwargs)

    @classmethod
    def get_tool_types(cls) -> Dict[str, Type[BaseTool]]:
        """Get registered tool types.

        Returns:
            Dict mapping tool type names to tool classes
        """
        return dict(cls._tool_types)

    @classmethod
    def clear(cls) -> None:
        """Clear all registered tool types."""
        cls._tool_types.clear()


# Register built-in tools
ToolFactory.register_tool_type(CurrentTimeTool)
