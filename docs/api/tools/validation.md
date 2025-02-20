# Validation Utilities

The `validation` module provides utility functions for validating tool schemas and parameters in the Bedrock Swarm framework. These functions ensure data integrity and type safety across tool operations.

## Module Documentation

::: bedrock_swarm.tools.validation
    options:
      show_root_heading: false
      show_source: true
      heading_level: 3

## Features

The validation utilities support:

1. Tool Schema Validation:
   - Validates tool name matches schema
   - Ensures schema structure is correct
   - Validates required fields

2. Parameter Validation:
   - JSON Schema validation
   - Required parameter checks
   - Type validation
   - Array validation
   - Custom validation rules

## Usage Examples

```python
from bedrock_swarm.tools.validation import validate_tool_schema, validate_tool_parameters

# Validate tool schema
schema = {
    "name": "my_tool",
    "parameters": {
        "type": "object",
        "properties": {
            "input": {"type": "string"},
            "count": {"type": "integer", "minimum": 0}
        },
        "required": ["input"]
    }
}

# Validate schema name matches tool name
validate_tool_schema("my_tool", schema)

# Validate parameters against schema
params = {
    "input": "test",
    "count": 5
}
validate_tool_parameters(schema, **params)
```

## Error Handling

The validation utilities handle:

1. Schema validation errors:
   - Tool name mismatches
   - Invalid schema structure
   - Missing required fields

2. Parameter validation errors:
   - Missing required parameters
   - Invalid parameter types
   - Array validation failures
   - Custom validation failures

## Implementation Details

The validation system uses:

1. JSON Schema validation through `jsonschema` library
2. Detailed error messages for debugging
3. Type checking and validation
4. Array validation support
5. Custom validation rules
