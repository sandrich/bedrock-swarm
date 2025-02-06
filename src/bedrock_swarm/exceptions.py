"""Exceptions for the bedrock-swarm package."""


class BedrockSwarmError(Exception):
    """Base exception class for bedrock-swarm."""

    pass


class ModelError(BedrockSwarmError):
    """Raised when there is an error with the model."""

    pass


class InvalidModelError(ModelError):
    """Raised when an invalid model ID is provided."""

    pass


class InvalidTemperatureError(ModelError):
    """Raised when an invalid temperature value is provided."""

    pass


class ModelInvokeError(BedrockSwarmError):
    """Raised when there is an error invoking a model."""

    pass


class ToolError(BedrockSwarmError):
    """Base class for tool-related errors."""

    pass


class ToolNotFoundError(ToolError):
    """Raised when a requested tool is not found."""

    pass


class ToolExecutionError(ToolError):
    """Raised when there is an error executing a tool."""

    pass


class ConfigError(BedrockSwarmError):
    """Raised when there is an error with the configuration."""

    pass


class AWSConfigError(ConfigError):
    """Raised when there is an error with AWS configuration."""

    pass


class ResponseParsingError(BedrockSwarmError):
    """Raised when there is an error parsing a model response."""

    pass


class AgencyError(BedrockSwarmError):
    """Raised when there is an error with agency operations."""

    pass


class ThreadError(BedrockSwarmError):
    """Raised when there is an error with thread operations."""

    pass
