"""Logging configuration for Bedrock Swarm."""

import logging


def configure_logging(level: str = "WARNING") -> None:
    """Configure logging with a standard format.

    Args:
        level (str, optional): Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL). Defaults to WARNING.
    """
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def set_log_level(level: str) -> None:
    """Set the log level for Bedrock Swarm.

    Args:
        level (str): Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    logger = logging.getLogger("bedrock_swarm")
    logger.setLevel(getattr(logging, level.upper()))
