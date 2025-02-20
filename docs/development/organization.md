# Code Organization

This document describes the organization and structure of the Bedrock Swarm codebase.

## Project Structure

```
bedrock-swarm/
├── bedrock_swarm/           # Main package directory
│   ├── __init__.py         # Package initialization
│   ├── agency/             # Agency components
│   │   ├── __init__.py
│   │   ├── agency.py       # Core agency implementation
│   │   ├── thread.py       # Thread management
│   │   └── events.py       # Event system
│   ├── agents/             # Agent implementations
│   │   ├── __init__.py
│   │   └── base.py        # Base agent class
│   ├── models/            # Model implementations
│   │   ├── __init__.py
│   │   ├── base.py       # Base model class
│   │   ├── claude.py     # Claude model
│   │   ├── titan.py      # Titan model
│   │   └── factory.py    # Model factory
│   └── tools/            # Tool implementations
│       ├── __init__.py
│       ├── base.py       # Base tool class
│       ├── calculator.py # Calculator tool
│       ├── time.py      # Time tool
│       └── validation.py # Validation tool
├── docs/                 # Documentation
├── tests/               # Test suite
├── examples/           # Example code
└── scripts/           # Development scripts
```

## Component Organization

### Agency Components

The `agency/` directory contains core orchestration components:

1. `agency.py`: Main agency implementation
2. `thread.py`: Thread management system
3. `events.py`: Event handling system

### Agent Components

The `agents/` directory contains agent implementations:

1. `base.py`: Base agent class
2. Custom agent implementations

### Model Components

The `models/` directory contains model implementations:

1. `base.py`: Base model interface
2. `claude.py`: Claude model implementation
3. `titan.py`: Titan model implementation
4. `factory.py`: Model factory system

### Tool Components

The `tools/` directory contains tool implementations:

1. `base.py`: Base tool interface
2. `calculator.py`: Calculator tool
3. `time.py`: Time tool
4. `validation.py`: Validation tool

## Code Style

We follow these organization principles:

1. **Module Organization**:
   - One class per file
   - Clear module names
   - Logical grouping

2. **Import Organization**:
   - Standard library first
   - Third-party imports second
   - Local imports last

3. **Code Structure**:
   - Clear class hierarchy
   - Consistent naming
   - Proper encapsulation

## Best Practices

1. **File Naming**:
   - Use lowercase
   - Use underscores
   - Be descriptive

2. **Module Structure**:
   - Module docstring
   - Imports
   - Constants
   - Classes
   - Functions

3. **Documentation**:
   - Clear docstrings
   - Type hints
   - Usage examples
