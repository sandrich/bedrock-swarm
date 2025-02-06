"""Tests for the tools factory module."""

from typing import Any, Dict, Generator, cast
from unittest.mock import MagicMock

import pytest

from bedrock_swarm.exceptions import ToolError
from bedrock_swarm.tools.base import BaseTool
from bedrock_swarm.tools.factory import ToolFactory


class MockTool(BaseTool):
    """Mock tool for testing."""

    def __init__(
        self, name: str = "mock_tool", description: str = "Mock tool for testing"
    ) -> None:
        """Initialize mock tool."""
        self._name = name
        self._description = description
        self._execute_mock = MagicMock(return_value="Tool result")

    @property
    def name(self) -> str:
        """Get tool name."""
        return self._name

    @property
    def description(self) -> str:
        """Get tool description."""
        return self._description

    def get_schema(self) -> Dict[str, Any]:
        """Get tool schema."""
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

    def _execute_impl(self, **kwargs: Any) -> str:
        """Execute the mock tool."""
        return cast(str, self._execute_mock(**kwargs))


@pytest.fixture(autouse=True)
def clear_registry() -> Generator[None, None, None]:
    """Clear tool registry before and after each test."""
    ToolFactory.clear()
    yield
    ToolFactory.clear()


def test_register_tool_type() -> None:
    """Test registering a tool type."""
    ToolFactory.register_tool_type(MockTool)
    assert "MockTool" in ToolFactory._tool_types
    assert ToolFactory._tool_types["MockTool"] == MockTool


def test_register_duplicate_tool_type() -> None:
    """Test registering a duplicate tool type."""
    ToolFactory.register_tool_type(MockTool)
    with pytest.raises(ToolError):
        ToolFactory.register_tool_type(MockTool)


def test_create_tool() -> None:
    """Test creating a tool."""
    ToolFactory.register_tool_type(MockTool)
    tool = ToolFactory.create_tool("MockTool", name="custom_tool")
    assert isinstance(tool, MockTool)
    assert tool.name == "custom_tool"


def test_create_nonexistent_tool() -> None:
    """Test creating a nonexistent tool."""
    with pytest.raises(ToolError):
        ToolFactory.create_tool("NonexistentTool")


def test_get_tool_types() -> None:
    """Test getting registered tool types."""
    ToolFactory.register_tool_type(MockTool)
    tool_types = ToolFactory.get_tool_types()
    assert "MockTool" in tool_types
    assert tool_types["MockTool"] == MockTool
