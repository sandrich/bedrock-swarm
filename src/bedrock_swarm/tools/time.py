"""Time-related tools."""

import logging
from datetime import datetime
from typing import Any, Dict, Optional
from zoneinfo import ZoneInfo, available_timezones

from .base import BaseTool

logger = logging.getLogger(__name__)


class CurrentTimeTool(BaseTool):
    """Tool for getting the current time and date."""

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
        """Get JSON schema for the tool."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "timezone": {
                        "type": "string",
                        "description": "Timezone name (e.g. 'UTC', 'US/Pacific', 'Asia/Tokyo'). Defaults to local timezone.",
                    },
                    "format": {
                        "type": "string",
                        "description": "Optional datetime format string (e.g. '%I:%M %p' for '1:46 PM'). If not provided, returns a natural format.",
                        "default": "%I:%M %p %Z",
                    },
                },
                "required": ["timezone"],
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
        timezone: str,
        format: str = "%I:%M %p %Z",
        **kwargs: Any,
    ) -> str:
        """Execute the time tool.

        Args:
            timezone: Timezone name
            format: Optional datetime format string
            **kwargs: Additional keyword arguments (unused)

        Returns:
            Formatted current time string

        Raises:
            ValueError: If timezone is invalid or format string is malformed
        """
        try:
            # Get current time in requested timezone
            tz_name = self._normalize_timezone(timezone)
            now = datetime.now(ZoneInfo(tz_name))

            # Format the time
            if format == "natural":
                return now.strftime("%I:%M %p %Z on %A, %B %d, %Y")
            elif format == "iso":
                return now.isoformat()
            else:
                return now.strftime(format)

        except Exception as e:
            raise ValueError(f"Error getting time: {str(e)}")
