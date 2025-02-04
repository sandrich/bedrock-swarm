"""Exceptions for the bedrock-swarm library."""

class BedrockSwarmError(Exception):
    """Base exception for all bedrock-swarm errors."""
    pass

class ModelError(BedrockSwarmError):
    """Raised when there is an error with the model."""
    pass

class InvalidModelError(ModelError):
    """Raised when an invalid model ID is provided."""
    pass

class ModelInvokeError(ModelError):
    """Raised when there is an error invoking the model."""
    pass

class ToolError(BedrockSwarmError):
    """Raised when there is an error with a tool."""
    pass

class ToolNotFoundError(ToolError):
    """Raised when a tool is not found."""
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
    """Raised when there is an error parsing the model response."""
    pass 