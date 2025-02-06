"""Integration tests for time tool."""

from datetime import datetime
from zoneinfo import ZoneInfo

from bedrock_swarm.tools.time import CurrentTimeTool


def test_time_tool_integration() -> None:
    """Test time tool with real time values."""
    tool = CurrentTimeTool()

    # Test default ISO format
    result = tool.execute()
    # Verify it's a valid ISO format string
    try:
        datetime.fromisoformat(result)
    except ValueError:
        raise AssertionError("Result is not a valid ISO format datetime")

    # Test custom format with current time
    before = datetime.now()
    result = tool.execute(format="%Y-%m-%d")
    after = datetime.now()
    assert before.strftime("%Y-%m-%d") == result == after.strftime("%Y-%m-%d")

    # Test timezone conversion
    local = tool.execute(format="%H:%M", timezone="local")
    utc = tool.execute(format="%H:%M", timezone="UTC")

    # Convert local time to UTC to verify the difference
    local_time = datetime.now()
    utc_time = local_time.astimezone(ZoneInfo("UTC"))

    # The hour difference should match
    local_hour = int(local.split(":")[0])
    utc_hour = int(utc.split(":")[0])
    expected_diff = (local_time.hour - utc_time.hour) % 24
    actual_diff = (local_hour - utc_hour) % 24
    assert expected_diff == actual_diff
