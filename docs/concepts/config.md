# Configuration System

The Bedrock Swarm configuration system provides a structured way to configure AWS credentials and other system settings.

## AWS Configuration

The primary configuration class is `AWSConfig`, which manages AWS credentials and settings:

```python
from bedrock_swarm.config import AWSConfig

# Basic configuration
config = AWSConfig(
    region="us-west-2"
)

# Configuration with profile
config = AWSConfig(
    region="us-west-2",
    profile="development"
)

# Configuration with custom endpoint
config = AWSConfig(
    region="us-west-2",
    profile="development",
    endpoint_url="https://custom.endpoint"
)
```

### Configuration Options

The `AWSConfig` class supports these options:

- `region` (required): The AWS region to use (e.g., "us-west-2")
- `profile` (optional): AWS profile name from your credentials file
- `endpoint_url` (optional): Custom endpoint URL for AWS services

## Usage with Agency

The configuration can be used when creating an agency:

```python
from bedrock_swarm.agency import Agency
from bedrock_swarm.config import AWSConfig

# Create AWS configuration
aws_config = AWSConfig(
    region="us-west-2",
    profile="development"
)

# Create agency with configuration
agency = Agency(
    aws_config=aws_config,
    agents=[...]
)
```

## Best Practices

1. **Environment Variables**: Use environment variables for sensitive information:
   ```bash
   export AWS_PROFILE=development
   export AWS_REGION=us-west-2
   ```

2. **Profile Management**: Use AWS profiles to manage multiple configurations:
   ```python
   # Development environment
   dev_config = AWSConfig(region="us-west-2", profile="development")

   # Production environment
   prod_config = AWSConfig(region="us-east-1", profile="production")
   ```

3. **Custom Endpoints**: Use custom endpoints for testing or special setups:
   ```python
   test_config = AWSConfig(
       region="us-west-2",
       endpoint_url="http://localhost:8000"
   )
   ```

## Security Considerations

1. Never hardcode AWS credentials in your code
2. Use IAM roles and temporary credentials when possible
3. Follow the principle of least privilege when setting up AWS permissions
4. Regularly rotate credentials and audit access

## Configuration Validation

The configuration system validates:
- Required region parameter
- Valid AWS region format
- Valid endpoint URL format (if provided)
- Profile name format (if provided)

## Error Handling

Common configuration errors:

```python
try:
    config = AWSConfig(region="invalid-region")
except ValueError as e:
    print(f"Invalid configuration: {e}")

try:
    config = AWSConfig(
        region="us-west-2",
        endpoint_url="invalid-url"
    )
except ValueError as e:
    print(f"Invalid endpoint URL: {e}")
```
