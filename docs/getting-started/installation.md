# Installation Guide

This guide will walk you through setting up Bedrock Swarm and configuring your AWS environment.

## Prerequisites

Before installing Bedrock Swarm, ensure you have:

1. **Python Environment**
   - Python 3.11 or later installed
   - pip (Python package manager)
   - (Optional) A virtual environment tool like `venv` or `conda`

2. **AWS Account Setup**
   - An AWS account with Bedrock access enabled
   - AWS CLI installed and configured
   - Appropriate IAM permissions for Bedrock

3. **Development Tools**
   - Git (for installation from source)
   - A text editor or IDE

## Step-by-Step Installation

### 1. Set Up Python Environment (Recommended)

```bash
# Create a new virtual environment
python -m venv bedrock-env

# Activate the environment
# On Windows:
bedrock-env\Scripts\activate
# On macOS/Linux:
source bedrock-env/bin/activate
```

### 2. Install Bedrock Swarm

Choose one of the following installation methods:

#### Using pip (Recommended)

```bash
# Basic installation
pip install bedrock-swarm

# With development tools (for contributing)
pip install "bedrock-swarm[dev]"

# With documentation tools (for building docs)
pip install "bedrock-swarm[docs]"
```

#### From Source

```bash
# Clone the repository
git clone https://github.com/yourusername/bedrock-swarm.git

# Change to the project directory
cd bedrock-swarm

# Install in editable mode
pip install -e .
```

### 3. Configure AWS Credentials

You have two options for configuring AWS credentials:

#### Option 1: Using AWS CLI (Recommended)

```bash
# Configure AWS credentials
aws configure

# Enter your credentials when prompted:
# AWS Access Key ID: your_access_key
# AWS Secret Access Key: your_secret_key
# Default region name: us-west-2
# Default output format: json
```

#### Option 2: Using Environment Variables

```bash
# On Windows (PowerShell)
$env:AWS_ACCESS_KEY_ID="your_access_key"
$env:AWS_SECRET_ACCESS_KEY="your_secret_key"
$env:AWS_REGION="us-west-2"

# On macOS/Linux
export AWS_ACCESS_KEY_ID="your_access_key"
export AWS_SECRET_ACCESS_KEY="your_secret_key"
export AWS_REGION="us-west-2"
```

## Verify Installation

Test your installation by running this simple script:

```python
from bedrock_swarm import BedrockAgent
from bedrock_swarm.config import AWSConfig

# Configure AWS
config = AWSConfig(
    region="us-west-2",
    profile="default"
)

# Create a test agent
agent = BedrockAgent(
    name="test",
    model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    aws_config=config,
    instructions="You are a test assistant."
)

# Test the agent
response = agent.process_message("Hello! Are you working?")
print(response)
```

## Common Issues and Solutions

### Installation Issues

1. **Python Version Error**
   ```
   ERROR: bedrock-swarm requires Python >=3.11
   ```
   Solution: Upgrade your Python installation or use pyenv to manage multiple Python versions.

2. **Dependency Conflicts**
   ```
   ERROR: Cannot install bedrock-swarm due to package conflicts
   ```
   Solution: Try installing in a fresh virtual environment.

### AWS Configuration Issues

1. **Missing AWS Credentials**
   ```
   botocore.exceptions.NoCredentialsError: Unable to locate credentials
   ```
   Solution: Ensure AWS credentials are properly configured using `aws configure` or environment variables.

2. **Bedrock Access Error**
   ```
   ClientError: An error occurred (AccessDeniedException)
   ```
   Solution: Verify your IAM user has the necessary Bedrock permissions.

3. **Region Not Enabled**
   ```
   ClientError: Bedrock is not available in region
   ```
   Solution: Choose a region where Bedrock is available (e.g., us-west-2, us-east-1).

## Next Steps

1. Follow the [Quick Start Guide](quickstart.md) to create your first agent
2. Learn about [AWS Configuration](configuration.md) for advanced settings
3. Explore [Basic Examples](../examples/basic.md) for common use cases

## Getting Help

If you encounter issues not covered here:

1. Check our [GitHub Issues](https://github.com/yourusername/bedrock-swarm/issues)
2. Ask on [Stack Overflow](https://stackoverflow.com/questions/tagged/bedrock-swarm)
3. Join our [Discord Community](https://discord.gg/bedrock-swarm)
