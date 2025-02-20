# Calculator Tool

The `CalculatorTool` provides mathematical calculation capabilities for agents in the Bedrock Swarm framework. It supports basic arithmetic operations, mathematical functions, and expression evaluation.

## Class Documentation

::: bedrock_swarm.tools.calculator.CalculatorTool
    options:
      show_root_heading: false
      show_source: true
      heading_level: 3

## Features

The calculator tool supports:

1. Basic arithmetic operations:
   - Addition (+)
   - Subtraction (-)
   - Multiplication (*)
   - Division (/)
   - Exponentiation (**)
   - Modulo (%)

2. Mathematical functions:
   - Square root (sqrt)
   - Absolute value (abs)
   - Trigonometric functions (sin, cos, tan)
   - Logarithms (log, ln)

## Usage Examples

```python
from bedrock_swarm.tools import CalculatorTool

calculator = CalculatorTool()

# Basic arithmetic
result = calculator.evaluate("2 + 2")
print(result)  # Output: 4

# Complex expressions
result = calculator.evaluate("sin(45) * sqrt(16)")
print(result)  # Output: 2.8284...

# Multiple operations
result = calculator.evaluate("(10 + 5) * 2 / 3")
print(result)  # Output: 10.0
```

## Error Handling

The calculator handles various error cases:

1. Invalid expressions
2. Division by zero
3. Invalid function calls
4. Type mismatches
5. Overflow/underflow

## Implementation Details

The calculator tool:

1. Parses mathematical expressions
2. Validates input safety
3. Handles numeric precision
4. Provides detailed error messages
5. Supports operator precedence
