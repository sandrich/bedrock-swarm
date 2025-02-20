# Base Model

The `BedrockModel` class serves as the foundation for all model implementations in the Bedrock Swarm framework. It defines the core interface and shared functionality that all model classes must implement.

## Class Documentation

::: bedrock_swarm.models.base.BedrockModel
    options:
      show_root_heading: true
      show_source: true

## Usage Example

```python
from bedrock_swarm.models.base import BedrockModel

class CustomModel(BedrockModel):
    def __init__(self, model_id: str, max_tokens: int):
        super().__init__(model_id=model_id, max_tokens=max_tokens)

    async def invoke(self, request: dict) -> AsyncGenerator[str, None]:
        # Custom implementation
        pass

    def format_request(self, request: dict) -> dict:
        # Custom implementation
        pass
```

## Error Handling

The base model provides several error handling mechanisms:

1. Token validation
2. Request format validation
3. Response parsing error handling

## Common Methods

All model implementations inherit these common methods:

- `validate_token_count`: Ensures the token count is within model limits
- `validate_temperature`: Validates temperature values are within acceptable range
- `parse_response`: Handles response parsing with error handling
- `format_request`: Template method for request formatting
- `invoke`: Abstract method for model invocation

## See Also

- [Claude Model](claude.md) - Claude model implementation
- [Titan Model](titan.md) - Titan model implementation
- [Model Factory](factory.md) - Model creation and configuration
- [Models Overview](index.md) - Overview of model system
