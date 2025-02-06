"""Exceptions for bedrock-swarm."""


class AgencyError(Exception):
    """Base exception for agency-related errors."""

    pass


class AgentError(Exception):
    """Base exception for agent-related errors."""

    pass


class ModelError(Exception):
    """Base exception for model-related errors."""

    pass


class ModelInvokeError(ModelError):
    """Exception raised when there is an error invoking a model."""

    pass


class ResponseParsingError(ModelError):
    """Exception raised when there is an error parsing a model response."""

    pass


class ToolError(Exception):
    """Base exception for tool-related errors."""

    pass


class ToolExecutionError(ToolError):
    """Exception raised when there is an error executing a tool."""

    pass


class BedrockSwarmError(Exception):
    """Base exception class for bedrock-swarm."""

    pass


class InvalidModelError(ModelError):
    """Raised when an invalid model ID is provided."""

    pass


class InvalidTemperatureError(ModelError):
    """Raised when an invalid temperature value is provided."""

    pass


class ConfigError(BedrockSwarmError):
    """Raised when there is an error with the configuration."""

    pass


class AWSConfigError(ConfigError):
    """Raised when there is an error with AWS configuration."""

    pass


class ToolNotFoundError(ToolError):
    """Raised when a requested tool is not found."""

    pass


class ThreadError(BedrockSwarmError):
    """Raised when there is an error with thread operations."""

    pass
