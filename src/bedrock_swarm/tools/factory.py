"""Tool factory for creating and managing tools."""

from typing import Any, Dict, List, Optional, Type

from ..exceptions import ToolError
from .base import BaseTool
from .web import WebSearchTool


class ToolFactory:
    """Factory class for creating and managing tools.

    This class provides a centralized way to create and manage tools.
    It maintains a registry of available tool types and their instances.
    """

    _tool_types: Dict[str, Type[BaseTool]] = {}
    _tool_instances: Dict[str, BaseTool] = {}

    @classmethod
    def register_tool_type(cls, tool_type: Type[BaseTool]) -> None:
        """Register a tool type.

        Args:
            tool_type (Type[BaseTool]): Tool type to register

        Raises:
            ToolError: If tool type is already registered
        """
        tool_name = tool_type.__name__
        if tool_name in cls._tool_types:
            raise ToolError(f"Tool type '{tool_name}' is already registered")
        cls._tool_types[tool_name] = tool_type

    @classmethod
    def create_tool(cls, tool_type_name: str, **kwargs: Any) -> BaseTool:
        """Create a tool instance.

        Args:
            tool_type_name (str): Name of the tool type to create
            **kwargs: Tool configuration parameters

        Returns:
            BaseTool: Created tool instance

        Raises:
            ToolError: If tool type is not registered
        """
        if tool_type_name not in cls._tool_types:
            raise ToolError(f"Tool type '{tool_type_name}' is not registered")

        tool_type = cls._tool_types[tool_type_name]
        tool = tool_type(**kwargs)

        # Store the instance if it's not already stored
        if tool.name not in cls._tool_instances:
            cls._tool_instances[tool.name] = tool

        return tool

    @classmethod
    def get_tool_types(cls) -> Dict[str, Type[BaseTool]]:
        """Get all registered tool types.

        Returns:
            Dict[str, Type[BaseTool]]: Dictionary mapping tool names to tool types
        """
        return cls._tool_types.copy()

    @classmethod
    def get_tool(cls, tool_name: str) -> Optional[BaseTool]:
        """Get a tool instance by name.

        Args:
            tool_name (str): Name of the tool to get

        Returns:
            Optional[BaseTool]: Tool instance if found, None otherwise
        """
        return cls._tool_instances.get(tool_name)

    @classmethod
    def get_all_tools(cls) -> List[BaseTool]:
        """Get all registered tool instances.

        Returns:
            List[BaseTool]: List of all tool instances
        """
        return list(cls._tool_instances.values())

    @classmethod
    def clear(cls) -> None:
        """Clear all registered tool types and instances."""
        cls._tool_types.clear()
        cls._tool_instances.clear()


# Register built-in tools
ToolFactory.register_tool_type(WebSearchTool)
