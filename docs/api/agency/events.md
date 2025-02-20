# Event System

The event system in Bedrock Swarm provides comprehensive tracking and monitoring of agent activities, tool executions, and system operations. It enables detailed tracing of operations and facilitates debugging and monitoring.

## Class Documentation

::: bedrock_swarm.events.EventSystem
    options:
      show_root_heading: false
      show_source: true
      heading_level: 3

## Event Types

The system supports these event types:

1. **Agent Events**:
   - `agent_start`: Agent begins processing
   - `agent_complete`: Agent completes processing
   - `message_sent`: Message sent between agents
   - `message_received`: Message received by agent

2. **Tool Events**:
   - `tool_start`: Tool execution begins
   - `tool_complete`: Tool execution completes
   - `tool_error`: Tool execution error

3. **Run Events**:
   - `run_start`: Run begins
   - `run_complete`: Run completes
   - `error`: Error occurred

## Event Structure

Each event follows this structure:

```python
{
    "id": "evt_123",              # Unique event ID
    "type": "agent_start",        # Event type
    "timestamp": "2024-02-29...", # ISO format timestamp
    "agent_name": "calculator",   # Name of agent involved
    "run_id": "run_456",         # ID of the run
    "thread_id": "thread_789",   # ID of the thread
    "parent_event_id": "evt_122", # ID of parent event
    "details": {                  # Event-specific details
        "message": "Processing request",
        "status": "active"
    },
    "metadata": {                # Additional metadata
        "version": "1.0",
        "environment": "prod"
    }
}
```

## Usage Examples

```python
from bedrock_swarm.agency import EventSystem

# Create event system
events = EventSystem()

# Record an event
event_id = events.record_event(
    type="agent_start",
    agent_name="calculator",
    run_id="run_123",
    thread_id="thread_456",
    details={"message": "Starting calculation"}
)

# Get event chain
chain = events.get_event_chain(event_id)
print(chain)  # Shows event and all related events

# Filter events
agent_events = events.filter_events(
    agent_name="calculator",
    event_type="tool_start"
)

# Get event trace
trace = events.get_trace(run_id="run_123")
print(trace)  # Shows complete trace of run
```

## Event Chains

Events can form parent-child relationships:

1. **Parent Events**:
   - Agent start events
   - Run start events
   - Tool start events

2. **Child Events**:
   - Tool execution events
   - Message events
   - Completion events

## Event Filtering

The system supports filtering by:

1. Event type
2. Agent name
3. Time range
4. Run ID
5. Thread ID

## Implementation Details

The event system provides:

1. **Event Recording**:
   - Unique ID generation
   - Timestamp management
   - Parent-child linking
   - Metadata attachment

2. **Event Retrieval**:
   - Chain reconstruction
   - Trace generation
   - Event filtering
   - Chronological ordering

3. **Event Analysis**:
   - Duration calculation
   - Success rate tracking
   - Performance monitoring
   - Error pattern detection

## Best Practices

1. **Event Recording**:
   ```python
   # Record start of operation
   start_id = events.record_event(
       type="operation_start",
       details={"operation": "calculation"}
   )

   try:
       # Perform operation
       result = perform_calculation()

       # Record success
       events.record_event(
           type="operation_complete",
           parent_id=start_id,
           details={"result": result}
       )
   except Exception as e:
       # Record error
       events.record_event(
           type="error",
           parent_id=start_id,
           details={"error": str(e)}
       )
   ```

2. **Event Monitoring**:
   ```python
   # Monitor specific agent
   agent_trace = events.get_agent_trace("calculator")

   # Monitor tool usage
   tool_events = events.filter_events(
       event_type="tool_start",
       tool_name="calculator"
   )

   # Monitor errors
   error_events = events.filter_events(
       event_type="error"
   )
   ```

3. **Performance Analysis**:
   ```python
   # Get operation duration
   duration = events.calculate_duration(
       start_event_id,
       end_event_id
   )

   # Get success rate
   success_rate = events.calculate_success_rate(
       agent_name="calculator"
   )
   ```
