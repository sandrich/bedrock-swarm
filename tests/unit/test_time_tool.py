"""Tests for the time tool."""

from datetime import datetime
from unittest.mock import patch
from zoneinfo import ZoneInfo

import pytest

from bedrock_swarm.exceptions import ToolError
from bedrock_swarm.tools.time import CurrentTimeTool


@pytest.fixture
def time_tool() -> CurrentTimeTool:
    """Create time tool for testing."""
    return CurrentTimeTool()


def test_tool_properties(time_tool: CurrentTimeTool) -> None:
    """Test basic tool properties."""
    assert time_tool.name == "current_time"
    assert "time" in time_tool.description.lower()

    schema = time_tool.get_schema()
    assert schema["name"] == "current_time"
    assert "format" in schema["parameters"]["properties"]
    assert "timezone" in schema["parameters"]["properties"]


@patch("bedrock_swarm.tools.time.datetime")
def test_default_format(mock_datetime: datetime, time_tool: CurrentTimeTool) -> None:
    """Test default ISO format."""
    mock_now = datetime(2024, 3, 14, 15, 9, 26)
    mock_datetime.now.return_value = mock_now

    result = time_tool.execute()
    assert result == "2024-03-14T15:09:26"


@patch("bedrock_swarm.tools.time.datetime")
def test_custom_format(mock_datetime: datetime, time_tool: CurrentTimeTool) -> None:
    """Test custom datetime format."""
    mock_now = datetime(2024, 3, 14, 15, 9, 26)
    mock_datetime.now.return_value = mock_now

    result = time_tool.execute(format="%Y-%m-%d %H:%M:%S")
    assert result == "2024-03-14 15:09:26"

    result = time_tool.execute(format="%A, %B %d, %Y")
    assert result == "Thursday, March 14, 2024"


def test_invalid_format(time_tool: CurrentTimeTool) -> None:
    """Test invalid format handling."""
    with pytest.raises(ToolError, match="Invalid datetime format"):
        time_tool.execute(format="%invalid")


@patch("bedrock_swarm.tools.time.datetime")
def test_timezone_conversion(
    mock_datetime: datetime, time_tool: CurrentTimeTool
) -> None:
    """Test timezone conversion."""
    mock_now = datetime(2024, 3, 14, 15, 9, 26, tzinfo=ZoneInfo("UTC"))
    mock_datetime.now.return_value = mock_now

    # Test UTC
    result = time_tool.execute(timezone="UTC", format="%H:%M:%S")
    assert result == "15:09:26"

    # Test specific timezone
    result = time_tool.execute(timezone="US/Pacific", format="%H:%M:%S")
    pacific_time = mock_now.astimezone(ZoneInfo("US/Pacific"))
    assert result == pacific_time.strftime("%H:%M:%S")


def test_invalid_timezone(time_tool: CurrentTimeTool) -> None:
    """Test invalid timezone handling."""
    with pytest.raises(ToolError, match="Invalid timezone"):
        time_tool.execute(timezone="InvalidZone")
