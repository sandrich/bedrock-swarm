# Examples

This directory contains example code demonstrating various features of Bedrock Swarm.

## Basic Examples

1. **Simple Time Tool**
   - Location: [basic.md#time-tool-example](basic.md#time-tool-example)
   - Shows how to use the built-in time tool
   - Demonstrates basic agent configuration
   - Includes error handling

2. **Custom Tool Creation**
   - Location: [basic.md#custom-tool-example](basic.md#custom-tool-example)
   - Demonstrates creating a custom tool
   - Shows tool validation and schema definition
   - Includes best practices

3. **Multi-Agent Workflow**
   - Location: [advanced.md#workflow-example](advanced.md#workflow-example)
   - Example of coordinating multiple agents
   - Shows workflow definition and execution
   - Includes input/output chaining

## Advanced Examples

1. **Thread Management**
   - Location: [advanced.md#thread-management](advanced.md#thread-management)
   - Managing conversation context
   - Thread creation and lifecycle
   - Memory management patterns

2. **Error Handling**
   - Location: [advanced.md#error-handling](advanced.md#error-handling)
   - Proper error handling patterns
   - Common error scenarios
   - Recovery strategies

3. **Token Tracking**
   - Location: [advanced.md#token-tracking](advanced.md#token-tracking)
   - Monitoring token usage
   - Cost optimization techniques
   - Usage reporting

## Example Categories

### By Feature
- Agent Creation and Configuration
- Tool Development and Usage
- Memory and Context Management
- Multi-Agent Coordination
- Error Handling and Recovery
- Performance Monitoring

### By Complexity
- Beginner: Basic agent setup and usage
- Intermediate: Custom tools and memory management
- Advanced: Multi-agent systems and workflows

## Running the Examples

1. **Prerequisites**
   - Complete the [Installation Guide](../getting-started/installation.md)
   - Configure AWS credentials
   - Install required dependencies

2. **Setup**
   ```bash
   # Install with examples dependencies
   pip install "bedrock-swarm[examples]"
   ```

3. **Running**
   ```bash
   # Navigate to examples directory
   cd examples

   # Run specific example
   python basic_time_tool.py
   ```

For more detailed examples and complete code samples, check out:
- [Basic Usage Guide](basic.md)
- [Advanced Patterns](advanced.md)
