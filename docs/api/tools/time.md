# Time Tool

The `CurrentTimeTool` provides time-related operations and utilities for agents in the Bedrock Swarm framework. It handles current time retrieval, timezone conversions, and time offsets.

## Class Documentation

::: bedrock_swarm.tools.time.CurrentTimeTool
    options:
      show_root_heading: false
      show_source: true
      heading_level: 3

## Features

The time tool provides:

1. Current time operations:
   - Get current time in any timezone
   - Support for timezone aliases (EST, PST, etc.)
   - Optional time offset in minutes

2. Time formatting:
   - ISO-like format (YYYY-MM-DD HH:MM:SS TZ)
   - Timezone information included

3. Timezone handling:
   - Support for all IANA timezone names
   - Common timezone aliases
   - Flexible timezone name matching

## Usage Examples

```python
from bedrock_swarm.tools import CurrentTimeTool

# Initialize the tool
time_tool = CurrentTimeTool()

# Get current time in local timezone
result = time_tool.execute()
print(result)  # Output: 2024-02-29 15:30:45 PST

# Get current time in UTC
result = time_tool.execute(timezone="UTC")
print(result)  # Output: 2024-02-29 23:30:45 UTC

# Get time with offset
result = time_tool.execute(timezone="EST", minutes_offset=30)
print(result)  # Output: 2024-02-29 18:00:45 EST

# Using timezone aliases
result = time_tool.execute(timezone="PST")  # Automatically maps to America/Los_Angeles
print(result)  # Output: 2024-02-29 15:30:45 PST
```

## Error Handling

The time tool handles various error cases:

1. Invalid timezone names
2. Timezone conversion errors
3. Invalid time offsets
4. General execution errors

## Implementation Details

The time tool:

1. Uses Python's `datetime` and `zoneinfo` libraries
2. Supports all IANA timezone names
3. Provides common timezone aliases
4. Includes timezone name normalization
5. Handles timezone-aware datetime objects
