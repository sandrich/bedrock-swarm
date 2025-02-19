"""Logging configuration for Bedrock Swarm."""

import logging
import sys
from typing import Optional


def configure_logging(
    level: str = "WARNING",
    format_string: Optional[str] = None,
    date_format: str = "%Y-%m-%d %H:%M:%S",
    handlers: Optional[list] = None,
) -> None:
    """Configure logging with a standard format.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL). Defaults to WARNING.
        format_string: Custom format string for log messages. If None, uses default format.
        date_format: Date format for timestamps. Defaults to ISO format.
        handlers: List of custom handlers. If None, uses StreamHandler to stdout.
    """
    # Default format if none provided
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Default handler if none provided
    if handlers is None:
        handlers = [logging.StreamHandler(sys.stdout)]

    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=format_string,
        datefmt=date_format,
        handlers=handlers,
    )

    # Configure bedrock_swarm logger
    logger = logging.getLogger("bedrock_swarm")
    logger.setLevel(getattr(logging, level.upper()))

    # Add handlers to bedrock_swarm logger
    for handler in handlers:
        handler.setFormatter(logging.Formatter(format_string, date_format))
        logger.addHandler(handler)


def set_log_level(level: str, logger_name: str = "bedrock_swarm") -> None:
    """Set the log level for a specific logger.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        logger_name: Name of the logger to configure. Defaults to bedrock_swarm.
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(getattr(logging, level.upper()))


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the bedrock_swarm namespace.

    Args:
        name: Name of the logger (will be prefixed with bedrock_swarm)

    Returns:
        Logger instance
    """
    return logging.getLogger(f"bedrock_swarm.{name}")
