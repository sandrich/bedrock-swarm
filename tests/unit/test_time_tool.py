"""Tests for time tool implementation."""

from datetime import datetime

import pytest

from bedrock_swarm.exceptions import ToolError
from bedrock_swarm.tools.time import CurrentTimeTool


@pytest.fixture
def time_tool() -> CurrentTimeTool:
    """Create a time tool instance."""
    return CurrentTimeTool()


def test_basic_time(time_tool: CurrentTimeTool) -> None:
    """Test basic time functionality."""
    # Test current time
    result = time_tool.execute()
    assert isinstance(result, str)
    assert len(result) > 0

    # Test with timezone
    result = time_tool.execute(timezone="UTC")
    assert "UTC" in result

    # Test with offset
    result = time_tool.execute(minutes_offset=60)
    current = datetime.now()
    result_time = datetime.strptime(result.rstrip(), "%Y-%m-%d %H:%M:%S")
    assert result_time.hour in [(current.hour + 1) % 24, current.hour]


def test_invalid_format(time_tool: CurrentTimeTool) -> None:
    """Test invalid format handling."""
    with pytest.raises(
        ToolError, match="Error getting time: 'No time zone found with key InvalidZone'"
    ):
        time_tool.execute(timezone="InvalidZone")


def test_invalid_timezone(time_tool: CurrentTimeTool) -> None:
    """Test invalid timezone handling."""
    with pytest.raises(
        ToolError, match="Error getting time: 'No time zone found with key InvalidZone'"
    ):
        time_tool.execute(timezone="InvalidZone")


def test_timezone_aliases(time_tool: CurrentTimeTool) -> None:
    """Test timezone aliases."""
    # Test common timezones
    result = time_tool.execute(timezone="America/Los_Angeles")
    assert "America/Los_Angeles" in result or "PDT" in result or "PST" in result

    result = time_tool.execute(timezone="America/New_York")
    assert "America/New_York" in result or "EDT" in result or "EST" in result


def test_timezone_normalization(time_tool: CurrentTimeTool) -> None:
    """Test timezone name normalization."""
    # Test case variations
    result = time_tool.execute(timezone="UTC")
    assert "UTC" in result

    result = time_tool.execute(timezone="GMT")
    assert "UTC" in result or "GMT" in result
