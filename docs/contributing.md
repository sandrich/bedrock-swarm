# Contributing Guide

Thank you for your interest in contributing to Bedrock Swarm! This document provides guidelines and instructions for contributing to the project.

## Getting Started

1. **Fork the Repository**
   ```bash
   git clone https://github.com/sandrich/bedrock-swarm.git
   cd bedrock-swarm
   ```

2. **Set Up Development Environment**
   ```bash
   # Create virtual environment
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # or
   .venv\Scripts\activate  # Windows

   # Install development dependencies
   pip install -e ".[dev]"
   ```

3. **Install Pre-commit Hooks**
   ```bash
   pre-commit install
   ```

## Development Workflow

1. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Write code following our style guide
   - Add tests for new functionality
   - Update documentation as needed

3. **Run Tests**
   ```bash
   # Run all tests
   pytest

   # Run specific test file
   pytest tests/test_your_feature.py

   # Run with coverage
   pytest --cov=bedrock_swarm
   ```

4. **Check Code Style**
   ```bash
   # Run pre-commit checks
   pre-commit run --all-files

   # Run flake8
   flake8 src/bedrock_swarm tests
   ```

5. **Build Documentation**
   ```bash
   # Install documentation dependencies
   pip install -e ".[docs]"

   # Build documentation
   mkdocs serve
   ```

## Pull Request Process

1. **Update Documentation**
   - Add docstrings for new functions/classes
   - Update relevant documentation files
   - Add example usage if applicable

2. **Write Tests**
   - Add unit tests for new functionality
   - Ensure all tests pass
   - Maintain or improve code coverage

3. **Submit PR**
   - Create PR against main branch
   - Fill out PR template
   - Request review from maintainers

## Code Style Guide

We follow these conventions:

1. **Python Style**
   - Follow PEP 8
   - Use type hints
   - Maximum line length: 88 characters
   - Use docstrings (Google style)

2. **Naming Conventions**
   ```python
   # Classes use CamelCase
   class MyClass:
       pass

   # Functions and variables use snake_case
   def my_function():
       my_variable = 42
   ```

3. **Documentation**
   ```python
   def my_function(param1: str, param2: int) -> bool:
       """Short description of function.

       Longer description if needed.

       Args:
           param1: Description of param1
           param2: Description of param2

       Returns:
           Description of return value

       Raises:
           ValueError: Description of when this is raised
       """
       pass
   ```

## Testing Guidelines

1. **Test Structure**
   ```python
   def test_my_feature():
       # Arrange
       input_data = "test"

       # Act
       result = my_function(input_data)

       # Assert
       assert result == expected_result
   ```

2. **Test Coverage**
   - Aim for 90%+ coverage
   - Test edge cases
   - Test error conditions

3. **Mocking**
   ```python
   from unittest.mock import Mock, patch

   @patch('bedrock_swarm.my_module.external_function')
   def test_with_mock(mock_external):
       mock_external.return_value = "mocked"
       result = my_function()
       assert result == "expected"
   ```

## Documentation Guidelines

1. **API Documentation**
   - Document all public APIs
   - Include type hints
   - Provide usage examples

2. **Example Code**
   - Make examples runnable
   - Keep examples simple
   - Include comments

3. **Markdown Style**
   - Use headers properly
   - Include code blocks
   - Add links where helpful

## Release Process

1. **Version Bump**
   - Update version in `pyproject.toml`
   - Update CHANGELOG.md
   - Create release commit

2. **Testing**
   - Run full test suite
   - Build documentation
   - Check package builds

3. **Release**
   - Create GitHub release
   - Build and upload to PyPI
   - Update documentation

## Getting Help

- Open an issue for bugs
- Start a discussion for questions
- Join our community channels

## Code of Conduct

Please note that this project is released with a [Code of Conduct](code_of_conduct.md). By participating in this project you agree to abide by its terms.
