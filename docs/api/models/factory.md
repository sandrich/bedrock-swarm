# Model Factory

The `ModelFactory` class provides a centralized way to create and manage model instances in the Bedrock Swarm framework. It handles model registration, configuration, and instantiation.

## Class Documentation

::: bedrock_swarm.models.factory.ModelFactory
    options:
      show_root_heading: false
      show_source: true
      heading_level: 3

## Model Registry

The model factory maintains a registry of available models and their configurations:

```python
BEDROCK_MODEL_REGISTRY = {
    "anthropic.claude-3-sonnet-20240229-v1:0": {
        "class": "ClaudeModel",
        "max_tokens": 200000
    },
    "anthropic.claude-v2:1": {
        "class": "ClaudeModel",
        "max_tokens": 100000
    },
    "amazon.titan-text-express-v1": {
        "class": "TitanModel",
        "max_tokens": 8000
    },
    "amazon.titan-text-lite-v1": {
        "class": "TitanModel",
        "max_tokens": 4000
    }
}
```

## Usage Example

```python
from bedrock_swarm.models import ModelFactory

# Create a model instance
model = ModelFactory.create_model("anthropic.claude-3-sonnet-20240229-v1:0")

# Use the model
request = {
    "prompt": "Hello, how can I help you today?",
    "temperature": 0.7
}

async for chunk in model.invoke(request):
    print(chunk)
```

## Error Handling

The factory includes error handling for:

1. Invalid model IDs
2. Missing model configurations
3. Model initialization errors

## Implementation Details

The factory implementation includes:

1. Model registration system
2. Configuration validation
3. Dynamic model instantiation
4. Error handling and logging
5. Model configuration management
