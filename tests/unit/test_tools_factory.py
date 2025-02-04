"""Tests for the tool factory."""
import pytest
from unittest.mock import Mock

from bedrock_swarm.tools.base import BaseTool
from bedrock_swarm.tools.factory import ToolFactory
from bedrock_swarm.tools.web import WebSearchTool
from bedrock_swarm.exceptions import ToolError

@pytest.fixture(autouse=True)
def clear_tool_registry():
    """Clear tool registry before each test."""
    ToolFactory.clear()
    yield
    ToolFactory.clear()

def test_register_tool_type():
    """Test registering a tool type."""
    # Create a mock tool type
    class MockTool(BaseTool):
        name = "mock_tool"
        description = "A mock tool"

        def get_schema(self):
            return {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            }

        async def execute(self, **kwargs):
            return "mock result"

    # Register the tool type
    ToolFactory.register_tool_type(MockTool)

    # Try to create a tool of this type
    tool = ToolFactory.create_tool("MockTool")
    assert isinstance(tool, MockTool)
    assert tool.name == "mock_tool"
    assert tool.description == "A mock tool"

def test_register_duplicate_tool_type():
    """Test that registering a duplicate tool type raises an error."""
    # Create a mock tool type
    class MockTool(BaseTool):
        name = "mock_tool"
        description = "A mock tool"
        
        async def execute(self, **kwargs):
            return "mock result"
    
    # Register the tool type once
    ToolFactory.register_tool_type(MockTool)
    
    # Try to register it again
    with pytest.raises(ToolError) as exc_info:
        ToolFactory.register_tool_type(MockTool)
    assert "is already registered" in str(exc_info.value)

def test_create_tool_with_params():
    """Test creating a tool with parameters."""
    # Create a mock tool type with parameters
    class MockTool(BaseTool):
        name = "mock_tool"
        description = "A mock tool"

        def __init__(self, custom_param: str):
            super().__init__()
            self.custom_param = custom_param

        def get_schema(self):
            return {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "custom_param": {"type": "string"}
                    }
                }
            }

        async def execute(self, **kwargs):
            return f"mock result with {self.custom_param}"

    # Register the tool type
    ToolFactory.register_tool_type(MockTool)

    # Create a tool instance with parameters
    tool = ToolFactory.create_tool("MockTool", custom_param="test")
    assert isinstance(tool, MockTool)
    assert tool.custom_param == "test"

def test_create_nonexistent_tool():
    """Test that creating a nonexistent tool type raises an error."""
    with pytest.raises(ToolError) as exc_info:
        ToolFactory.create_tool("NonexistentTool")
    assert "is not registered" in str(exc_info.value)

def test_get_tool():
    """Test getting a tool by name."""
    # Create a mock tool type
    class MockTool(BaseTool):
        name = "mock_tool"
        description = "A mock tool"

        def get_schema(self):
            return {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            }

        async def execute(self, **kwargs):
            return "mock result"

    # Register and create a tool
    ToolFactory.register_tool_type(MockTool)
    created_tool = ToolFactory.create_tool("MockTool")
    
    # Get the registered tool type
    assert "MockTool" in ToolFactory._tool_types
    assert ToolFactory._tool_types["MockTool"] == MockTool

def test_get_nonexistent_tool():
    """Test getting a nonexistent tool."""
    tool = ToolFactory.get_tool("nonexistent_tool")
    assert tool is None

def test_get_all_tools():
    """Test getting all tools."""
    # Create two mock tool types
    class MockTool1(BaseTool):
        name = "mock_tool_1"
        description = "A mock tool 1"

        def get_schema(self):
            return {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            }

        async def execute(self, **kwargs):
            return "mock result 1"

    class MockTool2(BaseTool):
        name = "mock_tool_2"
        description = "A mock tool 2"

        def get_schema(self):
            return {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            }

        async def execute(self, **kwargs):
            return "mock result 2"

    # Register and create both tools
    ToolFactory.register_tool_type(MockTool1)
    ToolFactory.register_tool_type(MockTool2)
    tool1 = ToolFactory.create_tool("MockTool1")
    tool2 = ToolFactory.create_tool("MockTool2")

    # Get all registered tool types
    tool_types = ToolFactory._tool_types
    assert "MockTool1" in tool_types
    assert "MockTool2" in tool_types
    assert tool_types["MockTool1"] == MockTool1
    assert tool_types["MockTool2"] == MockTool2

def test_clear_factory():
    """Test clearing the factory."""
    # Create a mock tool type
    class MockTool(BaseTool):
        name = "mock_tool"
        description = "A mock tool"

        def get_schema(self):
            return {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            }

        async def execute(self, **kwargs):
            return "mock result"

    # Register and create a tool
    ToolFactory.register_tool_type(MockTool)
    ToolFactory.create_tool("MockTool")

    # Clear the factory
    ToolFactory.clear()
    assert len(ToolFactory._tool_types) == 0

    # Try to create a tool after clearing
    with pytest.raises(ToolError, match="Tool type 'MockTool' is not registered"):
        ToolFactory.create_tool("MockTool")

def test_builtin_tools():
    """Test that built-in tools are registered."""
    # Register built-in tools
    from bedrock_swarm.tools.web import WebSearchTool
    ToolFactory.register_tool_type(WebSearchTool)
    
    # Create a web search tool
    tool = ToolFactory.create_tool("WebSearchTool")
    assert isinstance(tool, WebSearchTool)
    assert tool.name == "web_search" 