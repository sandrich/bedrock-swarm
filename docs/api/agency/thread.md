# Thread Management

The thread management system in Bedrock Swarm handles the execution and coordination of agent tasks. It provides mechanisms for creating, managing, and monitoring threads of execution.

## Class Documentation

::: bedrock_swarm.agency.thread.Thread
    options:
      show_root_heading: false
      show_source: true
      heading_level: 3

## Features

The thread system provides:

1. **Thread Creation**:
   - Dynamic thread creation
   - Thread configuration
   - Resource allocation

2. **Thread Management**:
   - Start/stop control
   - Pause/resume
   - Status monitoring
   - Resource cleanup

3. **Thread Communication**:
   - Message passing
   - Event handling
   - State synchronization

## Usage Examples

```python
from bedrock_swarm.agency import Thread

# Create a thread
thread = Thread(
    name="processing_thread",
    target=process_function,
    args=("input_data",),
    kwargs={"option": "value"}
)

# Start the thread
await thread.start()

# Check thread status
status = await thread.get_status()
print(status)  # Output: {"state": "running", "progress": 50}

# Send message to thread
await thread.send_message("update_config", {"param": "new_value"})

# Wait for completion
await thread.join()
```

## Thread States

Threads can be in these states:

1. **Created**: Initial state
2. **Running**: Active execution
3. **Paused**: Temporarily stopped
4. **Completed**: Finished execution
5. **Failed**: Error state

## Error Handling

The thread system handles:

1. Thread creation errors
2. Execution failures
3. Resource allocation errors
4. Communication errors
5. Cleanup failures

## Implementation Details

The thread implementation includes:

1. Async execution support
2. Resource management
3. Error recovery
4. State persistence
5. Performance monitoring

## Thread Configuration

Threads can be configured with:

```python
thread_config = {
    "name": "thread_name",
    "priority": "high",
    "timeout": 300,
    "retry_policy": {
        "max_retries": 3,
        "delay": 1.0
    },
    "resources": {
        "memory_limit": "1GB",
        "cpu_limit": 2
    }
}
```
