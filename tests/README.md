# Tests

This directory contains all tests for the bedrock-swarm library.

## Structure

```
tests/
├── unit/                  # Unit tests that mock external dependencies
│   └── bedrock_swarm/    # Tests matching the package structure
│       ├── agents/       # Tests for agent-related functionality
│       ├── agency/       # Tests for agency-related functionality
│       ├── models/       # Tests for model implementations
│       ├── tools/        # Tests for tool implementations
│       └── memory/       # Tests for memory implementations
└── integration/          # Integration tests with real dependencies
    └── bedrock_swarm/    # Tests matching the package structure
        ├── agents/       # Integration tests for agents
        ├── agency/       # Integration tests for agency
        ├── models/       # Integration tests for models
        └── tools/        # Integration tests for tools
```

## Running Tests

### Prerequisites

Install test dependencies:

```bash
pip install -r requirements-test.txt
```

### Running Unit Tests

```bash
# Run all unit tests
pytest tests/unit

# Run specific test file
pytest tests/unit/bedrock_swarm/models/test_base.py

# Run with coverage report
pytest --cov=bedrock_swarm --cov-report=term-missing --cov-report=html

# Run tests matching a pattern
pytest -k "test_agent"
```

### Running Integration Tests

Integration tests require AWS credentials and a valid AWS configuration.

```bash
# Run all integration tests
pytest tests/integration

# Run specific integration test
pytest tests/integration/bedrock_swarm/models/test_claude.py
```

## Coverage Requirements

The project maintains a minimum of 85% code coverage requirement. This is enforced in the CI/CD pipeline and can be checked locally using:

```bash
pytest --cov=bedrock_swarm --cov-report=term-missing --cov-fail-under=85
```

## Writing Tests

- Unit tests should mock all external dependencies (boto3, requests, etc.)
- Integration tests should test actual interactions with external services
- Follow the existing test structure and naming conventions
- Include docstrings explaining test purpose and setup
- Use appropriate fixtures for common setup
- Test both success and failure cases
