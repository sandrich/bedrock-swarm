# Installation Guide

## Prerequisites

- Python 3.8 or higher
- AWS account with Bedrock access
- AWS credentials configured

## Installation Methods

### Using pip

```bash
pip install bedrock-swarm
```

### Development Installation

For development or contributing:

```bash
git clone https://github.com/sandrich/bedrock-swarm
cd bedrock-swarm
pip install -e ".[dev]"
```

### Documentation Dependencies

To build documentation:

```bash
pip install "bedrock-swarm[docs]"
```

## Verifying Installation

You can verify your installation by running:

```python
from bedrock_swarm.agency import Agency
from bedrock_swarm.config import AWSConfig

# Should not raise any import errors
print(f"Bedrock Swarm installed successfully!")
```

## Troubleshooting

### Common Issues

1. **AWS Credentials Not Found**
   - Ensure AWS credentials are properly configured
   - Check `~/.aws/credentials` or environment variables

2. **Import Errors**
   - Verify Python version compatibility
   - Check for all required dependencies

3. **Bedrock Access**
   - Confirm your AWS account has Bedrock access
   - Verify IAM permissions are correctly set

For more help, please [open an issue](https://github.com/sandrich/bedrock-swarm/issues) on GitHub.
