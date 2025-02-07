"""Tests for validation module."""

import pytest

from bedrock_swarm.tools.validation import validate_tool_parameters


def test_basic_validation() -> None:
    """Test basic parameter validation."""
    schema = {
        "name": "test_tool",
        "description": "Test tool",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
            },
            "required": ["name"],
        },
    }

    # Valid parameters
    validate_tool_parameters(schema, name="John", age=30)

    # Valid with optional parameter missing
    validate_tool_parameters(schema, name="John")

    # Invalid: missing required parameter
    with pytest.raises(ValueError, match="Missing required parameter"):
        validate_tool_parameters(schema)

    # Invalid: wrong type
    with pytest.raises(ValueError):
        validate_tool_parameters(schema, name=123)


def test_nested_validation() -> None:
    """Test validation of nested objects."""
    schema = {
        "name": "test_tool",
        "description": "Test tool",
        "parameters": {
            "type": "object",
            "properties": {
                "person": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "address": {
                            "type": "object",
                            "properties": {
                                "street": {"type": "string"},
                                "city": {"type": "string"},
                            },
                            "required": ["street"],
                        },
                    },
                    "required": ["name", "address"],
                },
            },
            "required": ["person"],
        },
    }

    # Valid parameters
    validate_tool_parameters(
        schema,
        person={
            "name": "John",
            "address": {
                "street": "123 Main St",
                "city": "Springfield",
            },
        },
    )

    # Invalid: missing nested required field
    with pytest.raises(ValueError):
        validate_tool_parameters(
            schema,
            person={
                "name": "John",
                "address": {
                    "city": "Springfield",
                },
            },
        )


def test_array_validation() -> None:
    """Test validation of array parameters."""
    schema = {
        "name": "test_tool",
        "description": "Test tool",
        "parameters": {
            "type": "object",
            "properties": {
                "tags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 1,
                },
                "scores": {
                    "type": "array",
                    "items": {"type": "number"},
                },
            },
            "required": ["tags"],
        },
    }

    # Valid parameters
    validate_tool_parameters(schema, tags=["test", "demo"], scores=[1.0, 2.5, 3.0])

    # Invalid: empty array
    with pytest.raises(ValueError):
        validate_tool_parameters(schema, tags=[])

    # Invalid: wrong item type
    with pytest.raises(ValueError):
        validate_tool_parameters(schema, tags=["test", 123])


def test_enum_validation() -> None:
    """Test validation of enum parameters."""
    schema = {
        "name": "test_tool",
        "description": "Test tool",
        "parameters": {
            "type": "object",
            "properties": {
                "color": {
                    "type": "string",
                    "enum": ["red", "green", "blue"],
                },
                "size": {
                    "type": "string",
                    "enum": ["small", "medium", "large"],
                },
            },
            "required": ["color"],
        },
    }

    # Valid parameters
    validate_tool_parameters(schema, color="red", size="medium")

    # Invalid: value not in enum
    with pytest.raises(ValueError):
        validate_tool_parameters(schema, color="yellow")


def test_pattern_validation() -> None:
    """Test validation of pattern constraints."""
    schema = {
        "name": "test_tool",
        "description": "Test tool",
        "parameters": {
            "type": "object",
            "properties": {
                "email": {
                    "type": "string",
                    "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
                },
                "phone": {
                    "type": "string",
                    "pattern": "^\\d{3}-\\d{3}-\\d{4}$",
                },
            },
            "required": ["email"],
        },
    }

    # Valid parameters
    validate_tool_parameters(schema, email="test@example.com", phone="123-456-7890")

    # Invalid: wrong email format
    with pytest.raises(ValueError):
        validate_tool_parameters(schema, email="invalid-email")

    # Invalid: wrong phone format
    with pytest.raises(ValueError):
        validate_tool_parameters(schema, email="test@example.com", phone="1234567890")
