"""Time-related tools."""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from zoneinfo import ZoneInfo, available_timezones

from .base import BaseTool

logger = logging.getLogger(__name__)


class CurrentTimeTool(BaseTool):
    """Tool for getting current time and calculating future times."""

    def __init__(
        self,
        name: str = "current_time",
        description: str = "Get the current time and date in various formats and timezones",
    ) -> None:
        """Initialize the time tool.

        Args:
            name: Name of the tool
            description: Description of the tool
        """
        self._name = name
        self._description = description

    @property
    def name(self) -> str:
        """Get tool name."""
        return self._name

    @property
    def description(self) -> str:
        """Get tool description."""
        return self._description

    def get_schema(self) -> Dict[str, Any]:
        """Get JSON schema for the time tool."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "timezone": {
                        "type": "string",
                        "description": "Timezone to get time in (e.g. 'UTC', 'US/Pacific'). Defaults to local timezone.",
                    },
                    "minutes_offset": {
                        "type": "integer",
                        "description": "Optional number of minutes to add to current time",
                    },
                },
                "required": [],
            },
        }

    def _normalize_timezone(self, timezone: str) -> str:
        """Normalize timezone name.

        Args:
            timezone: Timezone name to normalize

        Returns:
            Normalized timezone name

        Raises:
            ValueError: If timezone is invalid
        """
        # Common aliases
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

        # Try alias first
        if timezone.upper() in aliases:
            return aliases[timezone.upper()]

        # Try as is
        if timezone in available_timezones():
            return timezone

        # Try common variations
        variations = [
            timezone,
            timezone.upper(),
            timezone.lower(),
            timezone.title(),
            f"Etc/{timezone}",
        ]

        for var in variations:
            if var in available_timezones():
                return var

        raise ValueError(f"Invalid timezone: {timezone}")

    def _execute_impl(
        self,
        *,
        timezone: Optional[str] = None,
        minutes_offset: Optional[int] = None,
        **kwargs: Any,
    ) -> str:
        """Execute the time tool.

        Args:
            timezone: Timezone to get time in (defaults to local timezone)
            minutes_offset: Optional number of minutes to add to current time

        Returns:
            Current or future time in specified timezone
        """
        try:
            # Use local timezone if none specified
            tz = None
            if timezone:
                normalized_tz = self._normalize_timezone(timezone)
                tz = ZoneInfo(normalized_tz)

            # Get current time in specified timezone
            current = datetime.now(tz)

            # Add offset if specified
            if minutes_offset is not None:
                current += timedelta(minutes=minutes_offset)

            # Format the time
            return current.strftime("%Y-%m-%d %H:%M:%S %Z")

        except Exception as e:
            raise ValueError(f"Error getting time: {str(e)}")
