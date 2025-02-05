"""Tool validation utilities."""

from typing import Any, Dict

import jsonschema


def validate_tool_schema(tool_name: str, schema: Dict[str, Any]) -> None:
    """Validate tool schema.

    Args:
        tool_name: Name of the tool
        schema: Tool schema

    Raises:
        ValueError: If schema is invalid
    """
    if schema["name"] != tool_name:
        raise ValueError("Schema name must match tool name")


def validate_tool_parameters(schema: Dict[str, Any], **kwargs: Any) -> None:
    """Validate parameters against tool schema.

    Args:
        schema: Tool schema
        **kwargs: Parameters to validate

    Raises:
        ValueError: If parameters are invalid
    """
    param_schema = schema["parameters"]

    try:
        jsonschema.validate(instance=kwargs, schema=param_schema)
    except jsonschema.exceptions.ValidationError as e:
        error_str = str(e)
        if "required" in error_str:
            raise ValueError("Missing required parameter") from e
        elif "minItems" in error_str:
            raise ValueError("Array must have at least 1 item") from e
        elif "type" in error_str:
            raise ValueError("Invalid parameter type") from e
        else:
            raise ValueError(f"Invalid parameters: {error_str}") from e
