# Logging System

The Bedrock Swarm logging system provides comprehensive logging capabilities for debugging, monitoring, and auditing agent operations.

## Basic Configuration

Configure logging with default settings:

```python
from bedrock_swarm.logging import configure_logging

# Basic configuration with default settings
configure_logging()  # Uses WARNING level by default

# Configure with specific log level
configure_logging(level="DEBUG")

# Configure with custom format
configure_logging(
    level="INFO",
    format_string="%(asctime)s - %(levelname)s - %(message)s",
    date_format="%Y-%m-%d %H:%M:%S"
)
```

## Log Levels

The system supports standard Python logging levels:
- `DEBUG`: Detailed information for debugging
- `INFO`: General information about program execution
- `WARNING`: Indicate a potential problem
- `ERROR`: A more serious problem
- `CRITICAL`: A critical error that may prevent the program from running

## Custom Handlers

You can configure custom log handlers:

```python
import logging
from logging.handlers import RotatingFileHandler
from bedrock_swarm.logging import configure_logging

# Create custom handlers
file_handler = RotatingFileHandler(
    "bedrock_swarm.log",
    maxBytes=1024*1024,  # 1MB
    backupCount=5
)
console_handler = logging.StreamHandler()

# Configure logging with custom handlers
configure_logging(
    level="DEBUG",
    handlers=[file_handler, console_handler]
)
```

## Logger Management

Get and configure specific loggers:

```python
from bedrock_swarm.logging import get_logger, set_log_level

# Get a logger for a specific component
logger = get_logger("agency")
logger.debug("Detailed debug information")
logger.info("General information")
logger.warning("Warning message")

# Change log level for specific logger
set_log_level("DEBUG", "bedrock_swarm.agency")
```

## Default Format

The default log format includes:
- Timestamp
- Logger name
- Log level
- Message

Example output:
```
2024-02-21 14:30:00 - bedrock_swarm.agency - INFO - Agency initialized
2024-02-21 14:30:01 - bedrock_swarm.agents - DEBUG - Processing request
2024-02-21 14:30:02 - bedrock_swarm.tools - WARNING - Tool execution timeout
```

## Best Practices

1. **Log Level Selection**:
   ```python
   # Development
   configure_logging(level="DEBUG")

   # Production
   configure_logging(level="WARNING")
   ```

2. **Component-Specific Logging**:
   ```python
   # Get loggers for different components
   agency_logger = get_logger("agency")
   agent_logger = get_logger("agents")
   tool_logger = get_logger("tools")

   # Log appropriate information
   agency_logger.info("Processing request")
   agent_logger.debug("Tool execution details")
   tool_logger.error("Tool execution failed")
   ```

3. **Error Tracking**:
   ```python
   try:
       # Some operation
       pass
   except Exception as e:
       logger.error(f"Operation failed: {str(e)}", exc_info=True)
   ```

## Integration with Event System

The logging system works alongside the event system:
- Events generate log entries
- Log entries provide additional context
- Both systems can be used for debugging

Example:
```python
# Event will be logged
agency.event_system.create_event(
    type="agent_start",
    agent_name="calculator",
    details={"request": "Calculate 2+2"}
)

# Log entry will be created
logger.info("Processing calculation request")
```
