# Titan Model

The `TitanModel` class provides an implementation for Amazon's Titan language models. It handles request formatting, response processing, and error handling specific to the Titan model family.

## Class Definition

::: bedrock_swarm.models.titan.TitanModel
    options:
      show_root_heading: true
      show_source: true

## Model Variants

The Titan model family includes several variants with different capabilities and token limits:

1. **Titan Text Express**
   - Model ID: `amazon.titan-text-express-v1`
   - Max Tokens: 8,000
   - Default Tokens: 2,048
   - Best for: General text generation and completion

2. **Titan Text Lite**
   - Model ID: `amazon.titan-text-lite-v1`
   - Max Tokens: 4,000
   - Default Tokens: 2,048
   - Best for: Lightweight text generation tasks

3. **Titan Text Premier**
   - Model ID: `amazon.titan-text-premier-v1:0`
   - Max Tokens: 3,072
   - Default Tokens: 2,048
   - Best for: High-quality text generation

## Request Format

The Titan model accepts requests in the following format:

```python
{
    "inputText": "Your message here",
    "textGenerationConfig": {
        "temperature": 0.7,  # 0.0 to 1.0
        "topP": 1,
        "maxTokenCount": 2048,
        "stopSequences": [],
    },
}
```

### Parameters

- `inputText` (str): The message to send to the model
- `temperature` (float): Controls randomness in generation (0.0 to 1.0)
- `maxTokenCount` (int): Maximum number of tokens to generate
- `system` (Optional[str]): System prompt to prepend to the message

## Response Format

The model returns responses in a streaming format:

```python
{
    "body": [
        {
            "chunk": {
                "bytes": b'{"outputText": "Model response part 1"}'
            }
        },
        {
            "chunk": {
                "bytes": b'{"outputText": "Model response part 2"}'
            }
        }
    ]
}
```

## Error Handling

The Titan model implementation includes comprehensive error handling:

1. **Token Validation**
   ```python
   # Raises ValueError if max_tokens exceeds model's limit
   request = model.format_request(message="Test", max_tokens=10000)
   ```

2. **Temperature Validation**
   ```python
   # Raises ValueError if temperature is outside 0.0-1.0 range
   request = model.format_request(message="Test", temperature=1.5)
   ```

3. **Response Parsing**
   ```python
   # Raises ResponseParsingError for invalid response format
   try:
       content = model._extract_content(response)
   except ResponseParsingError as e:
       print(f"Failed to parse response: {e}")
   ```

## Usage Example

```python
from bedrock_swarm.models.factory import ModelFactory

# Create Titan model instance
model = ModelFactory.create_model("amazon.titan-text-express-v1")

# Format request with system prompt
request = model.format_request(
    message="What is machine learning?",
    system="You are a helpful AI assistant.",
    temperature=0.7,
    max_tokens=1000
)

# Invoke model with retry handling
try:
    response = model.invoke(
        client=client,
        message="What is machine learning?"
    )
    print(response["content"])
except ModelInvokeError as e:
    print(f"Model invocation failed: {e}")
```

## Implementation Details

### Request Formatting

The `format_request` method handles:
- System prompt integration
- Temperature validation
- Token count validation
- Request structure formatting

### Response Processing

The `_extract_content` method:
- Decodes response chunks
- Extracts output text
- Handles JSON parsing errors
- Validates response format

### Retry Logic

The model uses exponential backoff for retries:
- Initial delay: 1 second
- Maximum retries: 5
- Handles rate limiting
- Retries on throttling errors

## Testing

The Titan model implementation includes comprehensive tests:

1. **Request Formatting**
   - Temperature validation
   - Token limit validation
   - System prompt integration

2. **Response Processing**
   - Chunk processing
   - Error handling
   - Content extraction

3. **Error Scenarios**
   - Invalid JSON
   - Missing fields
   - API errors
   - Rate limiting

## See Also

- [Base Model](base.md) - Base model implementation details
- [Model Factory](factory.md) - Model creation and configuration
- [Claude Model](claude.md) - Claude model implementation
