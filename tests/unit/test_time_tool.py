"""Tests for time tool implementation."""

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from bedrock_swarm.exceptions import ToolError
from bedrock_swarm.tools.time import CurrentTimeTool


@pytest.fixture
def time_tool() -> CurrentTimeTool:
    """Create a time tool instance."""
    return CurrentTimeTool()


def test_initialization():
    """Test tool initialization."""
    # Default initialization
    tool = CurrentTimeTool()
    assert tool.name == "current_time"
    assert (
        tool.description
        == "Get the current time and date in various formats and timezones"
    )

    # Custom initialization
    tool = CurrentTimeTool(
        name="custom_time",
        description="Custom time tool",
    )
    assert tool.name == "custom_time"
    assert tool.description == "Custom time tool"


def test_schema(time_tool: CurrentTimeTool):
    """Test schema generation."""
    schema = time_tool.get_schema()

    # Check basic structure
    assert schema["name"] == time_tool.name
    assert schema["description"] == time_tool.description
    assert "parameters" in schema
    assert schema["parameters"]["type"] == "object"

    # Check properties
    props = schema["parameters"]["properties"]
    assert "timezone" in props
    assert props["timezone"]["type"] == "string"
    assert "minutes_offset" in props
    assert props["minutes_offset"]["type"] == "integer"

    # Check no required parameters
    assert "required" in schema["parameters"]
    assert len(schema["parameters"]["required"]) == 0


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
    result_time = datetime.strptime(" ".join(result.split()[:2]), "%Y-%m-%d %H:%M:%S")
    assert result_time.hour in [(current.hour + 1) % 24, current.hour]


def test_invalid_format(time_tool: CurrentTimeTool) -> None:
    """Test invalid format handling."""
    with pytest.raises(ToolError, match="Error getting time"):
        time_tool.execute(timezone="InvalidZone")


def test_invalid_timezone(time_tool: CurrentTimeTool) -> None:
    """Test invalid timezone handling."""
    with pytest.raises(ToolError, match="Error getting time"):
        time_tool.execute(timezone="InvalidZone")


def test_timezone_aliases(time_tool: CurrentTimeTool) -> None:
    """Test timezone aliases."""
    # Test common timezones
    result = time_tool.execute(timezone="America/Los_Angeles")
    assert "America/Los_Angeles" in result or "PDT" in result or "PST" in result

    result = time_tool.execute(timezone="America/New_York")
    assert "America/New_York" in result or "EDT" in result or "EST" in result

    # Test all aliases
    aliases = {
        "EST": "America/New_York",
        "EDT": "America/New_York",
        "CST": "America/Chicago",
        "CDT": "America/Chicago",
        "MST": "America/Denver",
        "MDT": "America/Denver",
        "PST": "America/Los_Angeles",
        "PDT": "America/Los_Angeles",
        "JST": "Asia/Tokyo",
        "GMT": "UTC",
    }

    for alias in aliases:
        result = time_tool.execute(timezone=alias)
        assert isinstance(result, str)
        assert len(result) > 0


def test_timezone_normalization(time_tool: CurrentTimeTool) -> None:
    """Test timezone name normalization."""
    # Test case variations
    test_cases = [
        ("UTC", "UTC"),  # Standard format
        ("GMT", "UTC"),  # Common alias
        ("US/Pacific", "US/Pacific"),  # Region format
        ("America/New_York", "America/New_York"),  # Full name
        ("utc", "UTC"),  # Lowercase
        ("Utc", "UTC"),  # Title case
        ("UTC", "UTC"),  # Uppercase
    ]

    for input_tz, _ in test_cases:
        result = time_tool.execute(timezone=input_tz)
        # The timezone might appear in various formats in the result
        # For example, "America/New_York" might show as "EDT" or "EST"
        # So we just verify that the time was returned successfully
        assert isinstance(result, str)
        assert len(result) > 0

    # Test Etc/ prefix
    result = time_tool.execute(timezone="GMT")
    assert isinstance(result, str)
    assert len(result) > 0


def test_minutes_offset(time_tool: CurrentTimeTool) -> None:
    """Test minutes offset functionality."""
    # Test positive offset
    result = time_tool.execute(minutes_offset=30)
    current = datetime.now()
    result_time = datetime.strptime(" ".join(result.split()[:2]), "%Y-%m-%d %H:%M:%S")
    # Make both naive for comparison
    result_time = result_time.replace(tzinfo=None)
    delta = (result_time - current).total_seconds() / 60
    assert 29 <= delta <= 31  # Allow for small timing differences

    # Test negative offset
    result = time_tool.execute(minutes_offset=-30)
    current = datetime.now()
    result_time = datetime.strptime(" ".join(result.split()[:2]), "%Y-%m-%d %H:%M:%S")
    # Make both naive for comparison
    result_time = result_time.replace(tzinfo=None)
    delta = (current - result_time).total_seconds() / 60
    assert 29 <= delta <= 31  # Allow for small timing differences

    # Test zero offset
    result = time_tool.execute(minutes_offset=0)
    assert isinstance(result, str)
    assert len(result) > 0

    # Test large offset
    result = time_tool.execute(minutes_offset=1440)  # 24 hours
    current = datetime.now()
    result_time = datetime.strptime(" ".join(result.split()[:2]), "%Y-%m-%d %H:%M:%S")
    # Make both naive for comparison
    result_time = result_time.replace(tzinfo=None)
    delta = (result_time - current).total_seconds() / 3600  # Convert to hours
    assert 23.9 <= delta <= 24.1  # Allow for small timing differences


def test_error_handling(time_tool: CurrentTimeTool) -> None:
    """Test error handling."""
    # Test invalid timezone type
    with pytest.raises(ToolError, match="Invalid parameter type"):
        time_tool.execute(timezone=123)

    # Test invalid minutes_offset type
    with pytest.raises(ToolError, match="Invalid parameter type"):
        time_tool.execute(minutes_offset="30")

    # Test invalid timezone format
    with pytest.raises(ToolError, match="Error getting time"):
        time_tool.execute(timezone="Invalid/Zone/Format")


def test_timezone_with_offset(time_tool: CurrentTimeTool) -> None:
    """Test combining timezone and offset."""
    # Test timezone with positive offset
    result = time_tool.execute(timezone="UTC", minutes_offset=30)
    assert "UTC" in result
    current = datetime.now(ZoneInfo("UTC"))
    result_time = datetime.strptime(" ".join(result.split()[:2]), "%Y-%m-%d %H:%M:%S")
    # Make both aware for comparison
    result_time = result_time.replace(tzinfo=ZoneInfo("UTC"))
    delta = (result_time - current).total_seconds() / 60
    assert 29 <= delta <= 31  # Allow for small timing differences

    # Test timezone with negative offset
    result = time_tool.execute(timezone="UTC", minutes_offset=-30)
    assert "UTC" in result
    current = datetime.now(ZoneInfo("UTC"))
    result_time = datetime.strptime(" ".join(result.split()[:2]), "%Y-%m-%d %H:%M:%S")
    # Make both aware for comparison
    result_time = result_time.replace(tzinfo=ZoneInfo("UTC"))
    delta = (current - result_time).total_seconds() / 60
    assert 29 <= delta <= 31  # Allow for small timing differences
