"""Time-related tools."""

import logging
from datetime import datetime
from typing import Any, Dict, Optional
from zoneinfo import ZoneInfo

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
        super().__init__(name=name, description=description)

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
                    "format": {
                        "type": "string",
                        "description": "Optional datetime format string (e.g. '%Y-%m-%d %H:%M:%S'). If not provided, returns ISO format.",
                        "default": "iso",
                    },
                    "timezone": {
                        "type": "string",
                        "description": "Optional timezone name (e.g. 'UTC', 'US/Pacific'). Defaults to local timezone.",
                        "default": "local",
                    },
                },
            },
        }

    def _validate_format(self, fmt: str) -> None:
        """Validate datetime format string.

        Args:
            fmt: Format string to validate

        Raises:
            ValueError: If format string is invalid
        """
        logger.debug(f"Validating format string: {fmt}")

        # Check that the format string contains at least one valid directive
        valid_directives = {
            "%Y",
            "%m",
            "%d",
            "%H",
            "%M",
            "%S",
            "%I",
            "%p",
            "%B",
            "%b",
            "%A",
            "%a",
            "%j",
            "%U",
            "%W",
            "%c",
            "%x",
            "%X",
            "%w",
            "%Z",
            "%z",
        }

        if not any(directive in fmt for directive in valid_directives):
            logger.debug(f"Format string contains no valid directives: {fmt}")
            raise ValueError("Invalid datetime format")

        # Also try to use it with strftime to catch other errors
        test_date = datetime(2024, 1, 1)
        test_date.strftime(fmt)
        logger.debug("Format string validation successful")

    def _execute_impl(
        self,
        *,
        format: Optional[str] = None,
        timezone: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """Execute the time tool.

        Args:
            format: Optional datetime format string
            timezone: Optional timezone name
            **kwargs: Additional keyword arguments (unused)

        Returns:
            Formatted current time string

        Raises:
            ValueError: If timezone is invalid or format string is malformed
        """
        logger.debug(f"Executing time tool with kwargs: {kwargs}")

        # Get current time
        now = datetime.now()
        logger.debug(f"Current time: {now}")

        # Handle timezone
        tz = timezone or "local"
        logger.debug(f"Using timezone: {tz}")
        if tz != "local":
            try:
                now = now.astimezone(ZoneInfo(tz))
                logger.debug(f"Converted time to timezone: {now}")
            except (KeyError, ValueError):
                raise ValueError("Invalid timezone")

        # Handle format
        fmt = format or "iso"
        logger.debug(f"Using format: {fmt}")
        if fmt == "iso":
            result = now.isoformat()
            logger.debug(f"Returning ISO format: {result}")
            return result

        # Validate format string before using it
        self._validate_format(fmt)
        result = now.strftime(fmt)
        logger.debug(f"Returning formatted time: {result}")
        return result
