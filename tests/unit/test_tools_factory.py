"""Tests for the tools factory module."""

from unittest.mock import MagicMock

import pytest

from bedrock_swarm.exceptions import ToolError
from bedrock_swarm.tools.base import BaseTool
from bedrock_swarm.tools.factory import ToolFactory


class MockTool(BaseTool):
    """Mock tool for testing."""

    def __init__(self, name="mock_tool"):
        """Initialize mock tool."""
        super().__init__(name=name)
        self._execute_mock = MagicMock(return_value="Tool result")

    def execute(self, **kwargs):
        """Execute the tool."""
        return self._execute_mock(**kwargs)

    def get_schema(self):
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


def test_register_tool_type():
    """Test registering a tool type."""
    ToolFactory.register_tool_type(MockTool)
    assert "MockTool" in ToolFactory._tool_types
    assert ToolFactory._tool_types["MockTool"] == MockTool


def test_register_duplicate_tool_type():
    """Test registering a duplicate tool type."""
    ToolFactory.register_tool_type(MockTool)
    with pytest.raises(ToolError):
        ToolFactory.register_tool_type(MockTool)


def test_create_tool():
    """Test creating a tool."""
    ToolFactory.register_tool_type(MockTool)
    tool = ToolFactory.create_tool("MockTool", name="custom_tool")
    assert isinstance(tool, MockTool)
    assert tool.name == "custom_tool"


def test_create_nonexistent_tool():
    """Test creating a nonexistent tool."""
    with pytest.raises(ToolError):
        ToolFactory.create_tool("NonexistentTool")


def test_get_tool_types():
    """Test getting registered tool types."""
    ToolFactory.register_tool_type(MockTool)
    tool_types = ToolFactory.get_tool_types()
    assert "MockTool" in tool_types
    assert tool_types["MockTool"] == MockTool
