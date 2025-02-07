"""Tests for calculator tool implementation."""

import pytest

from bedrock_swarm.exceptions import ToolError
from bedrock_swarm.tools.calculator import CalculatorTool


@pytest.fixture
def calculator() -> CalculatorTool:
    """Create a calculator tool instance."""
    return CalculatorTool()


def test_basic_arithmetic(calculator: CalculatorTool) -> None:
    """Test basic arithmetic operations."""
    # Test addition
    result = calculator.execute(expression="2 + 2")
    assert result == "4"

    # Test subtraction
    result = calculator.execute(expression="5 - 3")
    assert result == "2"

    # Test multiplication
    result = calculator.execute(expression="4 * 3")
    assert result == "12"

    # Test division
    result = calculator.execute(expression="10 / 2")
    assert result == "5.0"


def test_complex_expressions(calculator: CalculatorTool) -> None:
    """Test more complex mathematical expressions."""
    # Test order of operations
    result = calculator.execute(expression="2 + 3 * 4")
    assert result == "14"

    # Test parentheses
    result = calculator.execute(expression="(2 + 3) * 4")
    assert result == "20"

    # Test floating point
    result = calculator.execute(expression="3.14 * 2")
    assert result == "6.28"


def test_invalid_expressions(calculator: CalculatorTool) -> None:
    """Test handling of invalid expressions."""
    # Test division by zero
    with pytest.raises(ToolError, match="Invalid expression: division by zero"):
        calculator.execute(expression="1/0")

    # Test invalid characters
    with pytest.raises(ToolError, match="Invalid characters in expression"):
        calculator.execute(expression="2 + abc")


def test_whitespace_handling(calculator: CalculatorTool) -> None:
    """Test handling of whitespace in expressions."""
    # Test no spaces
    result = calculator.execute(expression="2+2")
    assert result == "4"

    # Test extra spaces
    result = calculator.execute(expression="  2   +   2  ")
    assert result == "4"

    # Test invalid whitespace
    with pytest.raises(ToolError, match="Invalid characters in expression"):
        calculator.execute(expression="2 +\n2")
