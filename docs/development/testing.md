# Testing Strategy

This document outlines the testing strategy for Bedrock Swarm, including test organization, coverage requirements, and best practices.

## Test Organization

Tests are organized into the following categories:

1. **Unit Tests** (`tests/unit/`)
   - Test individual components in isolation
   - Mock external dependencies
   - Focus on edge cases and error handling

2. **Integration Tests** (`tests/integration/`)
   - Test component interactions
   - Use real AWS services
   - Verify end-to-end functionality

## Coverage Requirements

We maintain strict coverage requirements for different components:

### Core Components (95%+ coverage)
- Calculator Tool: 100%
- Events System: 100%
- Validation: 94%
- Time Tool: 95%
- Send Message Tool: 92%
- Agency: 91%

### Model Layer (80%+ coverage)
- Titan Model: 83%
- Claude Model: 36% (In Progress)
- Model Factory: 43% (In Progress)

### Supporting Components (60%+ coverage)
- Base Tools: 61%
- Memory System: 53%
- Base Agents: 33% (In Progress)
- Thread System: 18% (In Progress)

## Running Tests

### Basic Test Execution

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_model_titan.py

# Run with coverage
pytest --cov=bedrock_swarm

# Run with verbose output
pytest -v
```

### Test Configuration

The project uses `pytest.ini` for test configuration:

```ini
[pytest]
minversion = 6.0
addopts = -ra -q --cov=bedrock_swarm
testpaths = ["tests"]
markers =
    integration: marks tests as integration tests that should not be mocked
```

## Test Fixtures

Common test fixtures are defined in `tests/unit/conftest.py`:

1. **AWS Configuration**
   ```python
   @pytest.fixture(autouse=True)
   def mock_aws_session():
       """Mock AWS session for all unit tests."""
       with patch("boto3.Session") as mock_session:
           # Configure mock session
           yield mock_session
   ```

2. **Mock Tools**
   ```python
   @pytest.fixture
   def mock_tool():
       """Create a mock tool instance."""
       return MockTool()
   ```

3. **Mock Models**
   ```python
   @pytest.fixture
   def mock_model():
       """Create a mock model instance."""
       return MockBedrockModel()
   ```

## Best Practices

1. **Direct Method Testing**
   ```python
   def test_execute_impl():
       """Test direct method implementation."""
       tool = CalculatorTool()
       result = tool._execute_impl(expression="2 + 2")
       assert result == "4"
   ```

2. **Error Handling Tests**
   ```python
   def test_invalid_input():
       """Test error handling for invalid input."""
       with pytest.raises(ValueError, match="Invalid input"):
           tool.execute(invalid_param="value")
   ```

3. **Edge Cases**
   ```python
   def test_edge_cases():
       """Test edge cases and boundary conditions."""
       assert tool.execute(value=0) == "0"
       assert tool.execute(value=MAX_VALUE) == str(MAX_VALUE)
   ```

4. **Mocking External Services**
   ```python
   @patch("boto3.client")
   def test_aws_integration(mock_client):
       """Test AWS service integration."""
       mock_client.return_value.invoke_model.return_value = MOCK_RESPONSE
       result = model.invoke(message="test")
       assert result["content"] == "expected"
   ```

## Test Documentation

Each test file should include:

1. **Module Docstring**
   ```python
   """Tests for calculator tool implementation."""
   ```

2. **Test Function Docstrings**
   ```python
   def test_basic_arithmetic():
       """Test basic arithmetic operations."""
   ```

3. **Test Categories**
   ```python
   class TestCalculatorTool:
       """Tests for calculator tool functionality."""
   ```

## Continuous Integration

Tests are run automatically on:
- Pull request creation
- Push to main branch
- Daily scheduled runs

### CI Configuration

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: |
          pip install -e ".[test]"
          pytest --cov=bedrock_swarm
```

## Test Development Workflow

1. **Write Tests First**
   - Define expected behavior
   - Write test cases
   - Implement functionality

2. **Run Tests Locally**
   ```bash
   # Run tests with coverage
   pytest --cov=bedrock_swarm

   # Generate coverage report
   coverage html
   ```

3. **Review Coverage**
   - Identify uncovered code
   - Add missing test cases
   - Verify edge cases

4. **Update Documentation**
   - Document test changes
   - Update coverage requirements
   - Note any special cases

## See Also

- [Contributing Guidelines](contributing.md)
- [Code Organization](organization.md)
- [Tool Development](tools.md)
