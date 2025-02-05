"""Bedrock Swarm - A framework for building multi-agent systems using AWS Bedrock."""

from .agency.agency import Agency
from .agents.base import BedrockAgent
from .config import AWSConfig
from .exceptions import (
    AWSConfigError,
    ModelInvokeError,
    ResponseParsingError,
    ToolError,
)
from .logging import configure_logging, set_log_level
from .memory import BaseMemory, Message, SimpleMemory
from .tools.base import BaseTool
from .tools.web import WebSearchTool

# Configure default logging
configure_logging()

__all__ = [
    "Agency",
    "AWSConfig",
    "AWSConfigError",
    "BaseMemory",
    "BaseTool",
    "BedrockAgent",
    "Message",
    "ModelInvokeError",
    "ResponseParsingError",
    "SimpleMemory",
    "ToolError",
    "WebSearchTool",
    "configure_logging",
    "set_log_level",
]
