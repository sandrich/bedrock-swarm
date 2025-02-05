"""Logging configuration for Bedrock Swarm."""

import logging
import sys
from typing import Optional


def configure_logging(
    level: Optional[str] = None,
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
) -> None:
    """Configure logging for Bedrock Swarm.

    Args:
        level (Optional[str]): Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format (str): Log message format
    """
    # Get the root logger for bedrock_swarm
    logger = logging.getLogger("bedrock_swarm")

    # Set level (default to WARNING if not specified)
    log_level = getattr(logging, level.upper()) if level else logging.WARNING
    logger.setLevel(log_level)

    # Create console handler if none exists
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(log_level)

        # Create formatter
        formatter = logging.Formatter(format)
        handler.setFormatter(formatter)

        # Add handler to logger
        logger.addHandler(handler)


def set_log_level(level: str) -> None:
    """Set the log level for Bedrock Swarm.

    Args:
        level (str): Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    logger = logging.getLogger("bedrock_swarm")
    logger.setLevel(getattr(logging, level.upper()))
