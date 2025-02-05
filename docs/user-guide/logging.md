# Logging Guide

Bedrock Swarm provides built-in logging capabilities to help you monitor and debug your applications.

## Basic Usage

```python
from bedrock_swarm import configure_logging, set_log_level

# Configure logging with default settings (WARNING level)
configure_logging()

# Configure logging with custom level
configure_logging(level="DEBUG")

# Change log level at runtime
set_log_level("INFO")
```

## Log Levels

Available log levels (in order of increasing severity):

1. `DEBUG` - Detailed information for debugging
2. `INFO` - General information about program execution
3. `WARNING` - Warning messages for potentially problematic situations (default)
4. `ERROR` - Error messages for serious problems
5. `CRITICAL` - Critical errors that may prevent the program from running

## Configuration Options

### configure_logging()

Configure the logging system with custom settings:

```python
configure_logging(
    level="DEBUG",  # Log level (optional, defaults to WARNING)
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"  # Log format
)
```

Parameters:
- `level` (Optional[str]): Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `format` (str): Log message format string

### set_log_level()

Change the log level at runtime:

```python
set_log_level("DEBUG")  # Show all debug messages
set_log_level("WARNING")  # Show only warnings and above
```

## Example Output

Here's what the log messages look like with default formatting:

```
2024-03-20 10:15:30,123 - bedrock_swarm - DEBUG - Starting model invocation
2024-03-20 10:15:30,456 - bedrock_swarm - INFO - Created Bedrock client
2024-03-20 10:15:31,789 - bedrock_swarm - WARNING - Rate limit approaching
```

## Integration Example

Example of using logging in a complete application:

```python
from bedrock_swarm import (
    BedrockAgent,
    configure_logging,
    set_log_level,
    AWSConfig
)

def main():
    # Configure logging at startup
    configure_logging(level="DEBUG")

    # Create AWS config
    config = AWSConfig(
        region="us-west-2",
        profile="default"
    )

    # Create agent
    agent = BedrockAgent(
        name="assistant",
        model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        aws_config=config
    )

    try:
        # Process messages (debug logs will show details)
        response = agent.process_message("Hello!")
        print(response)

        # Change log level if needed
        set_log_level("INFO")

        response = agent.process_message("Another message")
        print(response)

    except Exception as e:
        # Error will be logged automatically
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
```

## Best Practices

1. **Development vs Production**
   - Use `DEBUG` level during development for detailed information
   - Use `WARNING` or `INFO` in production for important events
   - Use `ERROR` for capturing serious issues

2. **Log Level Selection**
   - `DEBUG`: Use for detailed troubleshooting
   - `INFO`: Use for general operational information
   - `WARNING`: Use for potential issues that don't affect core functionality
   - `ERROR`: Use for serious problems that affect functionality
   - `CRITICAL`: Use for fatal errors that prevent operation

3. **Performance Considerations**
   - Debug logging can impact performance
   - Consider using higher log levels in production
   - Use appropriate log levels for different environments

4. **Troubleshooting**
   - Start with `DEBUG` level when investigating issues
   - Look for patterns in log messages
   - Check timestamps for sequence of events

## Internal Logging

The framework uses logging internally to provide information about:

- Model invocations
- Client creation and configuration
- Tool execution
- Memory operations
- Error conditions

These logs can be controlled using the same configuration methods.
