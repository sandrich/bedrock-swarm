"""Tests for validation tool utilities."""

import pytest

from bedrock_swarm.tools.validation import (
    validate_tool_parameters,
    validate_tool_schema,
)


def test_validate_tool_schema():
    """Test tool schema validation."""
    # Valid schema
    valid_schema = {
        "name": "test_tool",
        "description": "Test tool",
        "parameters": {
            "type": "object",
            "properties": {
                "param1": {"type": "string"},
            },
            "required": ["param1"],
        },
    }
    validate_tool_schema("test_tool", valid_schema)  # Should not raise

    # Schema name mismatch
    invalid_schema = valid_schema.copy()
    invalid_schema["name"] = "wrong_name"
    with pytest.raises(ValueError, match="Schema name must match tool name"):
        validate_tool_schema("test_tool", invalid_schema)


def test_validate_tool_parameters_required():
    """Test validation of required parameters."""
    schema = {
        "name": "test_tool",
        "parameters": {
            "type": "object",
            "properties": {
                "required_param": {"type": "string"},
                "optional_param": {"type": "number"},
            },
            "required": ["required_param"],
        },
    }

    # Missing required parameter
    with pytest.raises(ValueError, match="Missing required parameter"):
        validate_tool_parameters(schema)

    # With required parameter
    validate_tool_parameters(schema, required_param="test")  # Should not raise

    # With both parameters
    validate_tool_parameters(
        schema, required_param="test", optional_param=42
    )  # Should not raise


def test_validate_tool_parameters_types():
    """Test validation of parameter types."""
    schema = {
        "name": "test_tool",
        "parameters": {
            "type": "object",
            "properties": {
                "string_param": {"type": "string"},
                "number_param": {"type": "number"},
                "boolean_param": {"type": "boolean"},
                "array_param": {"type": "array", "items": {"type": "string"}},
                "object_param": {"type": "object"},
            },
            "required": ["string_param"],
        },
    }

    # Valid types
    validate_tool_parameters(
        schema,
        string_param="test",
        number_param=42,
        boolean_param=True,
        array_param=["one", "two"],
        object_param={"key": "value"},
    )

    # Invalid string type
    with pytest.raises(ValueError, match="Invalid parameter type"):
        validate_tool_parameters(schema, string_param=123)

    # Invalid number type
    with pytest.raises(ValueError, match="Invalid parameter type"):
        validate_tool_parameters(
            schema, string_param="test", number_param="not_a_number"
        )

    # Invalid boolean type
    with pytest.raises(ValueError, match="Invalid parameter type"):
        validate_tool_parameters(
            schema, string_param="test", boolean_param="not_a_boolean"
        )

    # Invalid array type
    with pytest.raises(ValueError, match="Invalid parameter type"):
        validate_tool_parameters(
            schema, string_param="test", array_param="not_an_array"
        )

    # Invalid array item type
    with pytest.raises(ValueError, match="Invalid parameter type"):
        validate_tool_parameters(schema, string_param="test", array_param=[1, 2, 3])

    # Invalid object type
    with pytest.raises(ValueError, match="Invalid parameter type"):
        validate_tool_parameters(
            schema, string_param="test", object_param="not_an_object"
        )


def test_validate_tool_parameters_array_constraints():
    """Test validation of array constraints."""
    schema = {
        "name": "test_tool",
        "parameters": {
            "type": "object",
            "properties": {
                "array_param": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 1,
                    "maxItems": 3,
                },
            },
            "required": ["array_param"],
        },
    }

    # Valid array length
    validate_tool_parameters(schema, array_param=["one"])  # Should not raise
    validate_tool_parameters(schema, array_param=["one", "two"])  # Should not raise
    validate_tool_parameters(
        schema, array_param=["one", "two", "three"]
    )  # Should not raise

    # Empty array
    with pytest.raises(ValueError, match="Array must have at least 1 item"):
        validate_tool_parameters(schema, array_param=[])
