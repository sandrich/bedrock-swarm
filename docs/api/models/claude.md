# Claude Model

The `ClaudeModel` class implements the interface for Amazon's Claude language models, providing access to various Claude model versions through Amazon Bedrock.

## Class Documentation

::: bedrock_swarm.models.claude.ClaudeModel
    options:
      show_root_heading: true
      show_source: true

## Model Variants

The following Claude model variants are supported:

- **Claude 3.5 Sonnet**: Latest general purpose model with strong performance across tasks
  - Model ID: `us.anthropic.claude-3-5-sonnet-20241022-v2:0`
  - Best for: Complex reasoning, analysis, and generation tasks

## Request Format

```python
request = {
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 4096,  # Optional, defaults to 4096
    "temperature": 0.7,  # Optional, defaults to 0.7
    "messages": [
        {
            "role": "user",
            "content": "Your message here"
        }
    ]
}
```

## Response Format

The model returns responses in a streaming format with content blocks:

```python
async for chunk in model.invoke(request):
    # Each chunk contains a content block delta
    print(chunk)  # Process each chunk as it arrives
```

## Error Handling

The Claude model implementation includes comprehensive error handling for:

1. Token validation (enforces model-specific limits)
2. Temperature validation (must be between 0 and 1)
3. Response parsing (handles various response formats)
4. API errors (with automatic retries)

## Usage Example

```python
from bedrock_swarm.models import ClaudeModel

model = ClaudeModel()

request = model.format_request(
    message="Explain quantum computing in simple terms.",
    temperature=0.7,
    max_tokens=1000
)

async for chunk in model.invoke(request):
    print(chunk)
```

## Implementation Details

The Claude model implementation includes:

1. Request formatting according to Claude's specifications
2. Response streaming with chunk processing
3. Automatic retry logic for transient errors
4. Comprehensive error handling
5. Token limit enforcement

## See Also

- [Base Model](base.md) - Base model implementation details
- [Model Factory](factory.md) - Model creation and configuration
- [Titan Model](titan.md) - Titan model implementation
- [Models Overview](index.md) - Overview of model system
