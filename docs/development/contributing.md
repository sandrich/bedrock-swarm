# Contributing Guide

This guide explains how to contribute to the Bedrock Swarm framework. We welcome contributions of all kinds, from bug fixes to new features.

## Getting Started

1. **Fork the Repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/bedrock-swarm.git
   cd bedrock-swarm
   ```

2. **Set Up Development Environment**
   ```bash
   # Create virtual environment
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # or
   .venv\Scripts\activate  # Windows

   # Install dependencies
   pip install -e ".[dev]"
   ```

3. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Workflow

1. **Code Style**
   - Follow PEP 8
   - Use type hints
   - Write docstrings (Google style)
   - Keep functions focused

2. **Testing**
   - Write unit tests
   - Include integration tests
   - Maintain coverage (90%+)
   - Test edge cases

3. **Documentation**
   - Update API docs
   - Add examples
   - Include docstrings
   - Update changelog

## Testing

Run tests with:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=bedrock_swarm

# Run specific test file
pytest tests/unit/test_agency.py

# Run with verbose output
pytest -v
```

## Documentation

Build documentation with:

```bash
# Install documentation dependencies
pip install -e ".[docs]"

# Build documentation
mkdocs build

# Serve documentation locally
mkdocs serve
```

## Code Quality

Maintain code quality with:

```bash
# Format code
black .

# Sort imports
isort .

# Check types
mypy .

# Run linter
flake8 .
```

## Pull Request Process

1. **Update Documentation**
   - Add/update API documentation
   - Update README if needed
   - Add examples for new features

2. **Run Tests**
   - Ensure all tests pass
   - Add new tests as needed
   - Maintain coverage

3. **Update Changelog**
   - Add entry to CHANGELOG.md
   - Follow Keep a Changelog format
   - Include PR number

4. **Submit PR**
   - Create detailed description
   - Link related issues
   - Request review

## Commit Guidelines

Follow conventional commits:

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation
- style: Formatting
- refactor: Code restructuring
- test: Adding tests
- chore: Maintenance

Example:
```
feat(agency): add thread pooling system

- Implements thread reuse
- Adds configuration options
- Updates documentation

Closes #123
```

## Release Process

1. **Version Bump**
   ```bash
   # Update version in pyproject.toml
   # Update CHANGELOG.md
   # Create release commit
   git commit -m "chore: release v1.2.3"
   ```

2. **Create Tag**
   ```bash
   git tag -a v1.2.3 -m "Version 1.2.3"
   git push origin v1.2.3
   ```

3. **Build Package**
   ```bash
   python -m build
   ```

4. **Publish Release**
   ```bash
   python -m twine upload dist/*
   ```

## Code Review

Guidelines for reviewers:

1. **Code Quality**
   - Clean and readable
   - Well-documented
   - Properly tested
   - Type safe

2. **Architecture**
   - Follows patterns
   - Maintainable
   - Performant
   - Secure

3. **Documentation**
   - Clear and complete
   - Includes examples
   - Up to date
   - Well-structured

## Community

- **Issues**: Use issue templates
- **Discussions**: Use GitHub Discussions
- **Questions**: Use issue tracker
- **Security**: Report privately

## License

By contributing, you agree that your contributions will be licensed under the project's MIT License.
