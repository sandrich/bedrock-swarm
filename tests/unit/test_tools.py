"""Tests for the tools functionality."""

from typing import Any, Dict
from unittest.mock import MagicMock

import pytest

from bedrock_swarm.tools.base import BaseTool


@pytest.fixture
def clear_tool_registry() -> None:
    """Clear the tool registry before and after each test."""
    BaseTool._registry = {}  # type: ignore
    yield
    BaseTool._registry = {}  # type: ignore


class MockTool(BaseTool):
    """Mock tool for testing."""

    def __init__(self, name: str, description: str) -> None:
        """Initialize the mock tool."""
        super().__init__(name=name, description=description)
        self._execute_mock = MagicMock(return_value="Mock result")

    @property
    def name(self) -> str:
        """Get tool name."""
        return self._name

    @property
    def description(self) -> str:
        """Get tool description."""
        return self._description

    def get_schema(self) -> Dict[str, Any]:
        """Get the schema for the mock tool."""
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
        return self._execute_mock(**kwargs)


def test_base_tool():
    """Test base tool functionality."""
    tool = MockTool(name="mock_tool", description="Mock tool")
    assert tool.name == "mock_tool"
    assert isinstance(tool.get_schema(), dict)


def test_tool_execution():
    """Test tool execution."""
    tool = MockTool(name="mock_tool", description="Mock tool")
    result = tool.execute(param1="test", param2=123)
    assert result == "Mock result"
    tool._execute_mock.assert_called_once_with(param1="test", param2=123)
