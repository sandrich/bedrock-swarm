"""Bedrock Swarm - A framework for building multi-agent systems using AWS Bedrock."""

from .agency.agency import Agency
from .agents.base import BedrockAgent
from .config import AWSConfig
from .exceptions import (
    AgencyError,
    AgentError,
    ModelError,
    ModelInvokeError,
    ResponseParsingError,
    ToolError,
    ToolExecutionError,
)
from .logging import configure_logging
from .models.claude import Claude35Model
from .tools.base import BaseTool
from .tools.time import CurrentTimeTool

# Configure default logging
configure_logging()

__all__ = [
    "Agency",
    "BedrockAgent",
    "AWSConfig",
    "configure_logging",
    "AgencyError",
    "AgentError",
    "ModelError",
    "ModelInvokeError",
    "ResponseParsingError",
    "ToolError",
    "ToolExecutionError",
    "Claude35Model",
    "BaseTool",
    "CurrentTimeTool",
]
