# API Reference

This section provides detailed API documentation for Bedrock Swarm.

## Core Components

- [Agency](agency.md) - Multi-agent orchestration and thread management
- [Agents](agency/agents.md) - Agent implementations and base classes
- [Tools](tools.md) - Built-in and base tool implementations
- [Events](agency/events.md) - Event system for tracing and monitoring
- [Memory](agency/memory.md) - Memory systems for context management

## Models

- [Base Model](models/base.md) - Base model implementation and utilities
- [Titan Model](models/titan.md) - Amazon Titan model implementation
- [Claude Model](models/claude.md) - Anthropic Claude model implementation
- [Model Factory](models/factory.md) - Model creation and configuration

## Tools

- [Calculator](tools/calculator.md) - Mathematical calculation tool
- [Time](tools/time.md) - Time and timezone operations
- [Send Message](tools/send_message.md) - Inter-agent communication
- [Validation](tools/validation.md) - Tool parameter validation utilities

## Agency Components

- [Thread](agency/thread.md) - Thread management and execution
- [Run](agency/run.md) - Run lifecycle and state management
- [Event System](agency/events.md) - Event tracking and monitoring

## Development

- [Testing](../development/testing.md) - Testing strategy and coverage
- [Contributing](../development/contributing.md) - Contribution guidelines
- [Code Organization](../development/organization.md) - Project structure
- [Tool Development](../development/tools.md) - Creating custom tools
