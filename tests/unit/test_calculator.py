"""Tests for calculator tool implementation."""

import pytest

from bedrock_swarm.tools.calculator import CalculatorTool


@pytest.fixture
def calculator() -> CalculatorTool:
    """Create a calculator tool instance."""
    return CalculatorTool()


def test_initialization():
    """Test calculator tool initialization."""
    # Default initialization
    calc = CalculatorTool()
    assert calc.name == "calculator"
    assert calc.description == "Perform basic arithmetic calculations"

    # Custom initialization
    calc = CalculatorTool(name="custom_calc", description="Custom calculator")
    assert calc.name == "custom_calc"
    assert calc.description == "Custom calculator"


def test_schema():
    """Test calculator tool schema."""
    calc = CalculatorTool()
    schema = calc.get_schema()

    assert schema["name"] == "calculator"
    assert schema["description"] == "Perform basic arithmetic calculations"
    assert "parameters" in schema
    assert schema["parameters"]["type"] == "object"
    assert "expression" in schema["parameters"]["properties"]
    assert schema["parameters"]["required"] == ["expression"]


def test_basic_arithmetic():
    """Test basic arithmetic operations."""
    calc = CalculatorTool()

    # Addition
    assert calc._execute_impl(expression="2 + 2") == "4"
    assert calc._execute_impl(expression="0 + 0") == "0"
    assert calc._execute_impl(expression="-1 + 1") == "0"

    # Subtraction
    assert calc._execute_impl(expression="5 - 3") == "2"
    assert calc._execute_impl(expression="0 - 0") == "0"
    assert calc._execute_impl(expression="-1 - -1") == "0"

    # Multiplication
    assert calc._execute_impl(expression="3 * 4") == "12"
    assert calc._execute_impl(expression="0 * 5") == "0"
    assert calc._execute_impl(expression="-2 * 3") == "-6"

    # Division
    assert calc._execute_impl(expression="8 / 2") == "4.0"
    assert calc._execute_impl(expression="1 / 2") == "0.5"
    assert calc._execute_impl(expression="-6 / 2") == "-3.0"


def test_complex_expressions():
    """Test more complex arithmetic expressions."""
    calc = CalculatorTool()

    # Parentheses and order of operations
    assert calc._execute_impl(expression="2 + 3 * 4") == "14"
    assert calc._execute_impl(expression="(2 + 3) * 4") == "20"
    assert calc._execute_impl(expression="2 * (3 + 4)") == "14"

    # Multiple operations
    assert calc._execute_impl(expression="1 + 2 + 3") == "6"
    assert calc._execute_impl(expression="10 - 5 + 2") == "7"
    assert calc._execute_impl(expression="2 * 3 * 4") == "24"

    # Decimals
    assert calc._execute_impl(expression="1.5 + 2.5") == "4.0"
    assert calc._execute_impl(expression="3.0 * 2") == "6.0"


def test_invalid_expressions():
    """Test handling of invalid expressions."""
    calc = CalculatorTool()

    # Invalid characters
    with pytest.raises(ValueError, match="Invalid characters in expression"):
        calc._execute_impl(expression="2 + a")
    with pytest.raises(ValueError, match="Invalid characters in expression"):
        calc._execute_impl(expression="print(2)")
    with pytest.raises(ValueError, match="Invalid characters in expression"):
        calc._execute_impl(expression="os.system('ls')")

    # Invalid syntax
    with pytest.raises(ValueError, match="Invalid expression"):
        calc._execute_impl(expression="2 +")
    with pytest.raises(ValueError, match="Invalid expression"):
        calc._execute_impl(expression="* 2")

    # Division by zero
    with pytest.raises(ValueError, match="Invalid expression"):
        calc._execute_impl(expression="1/0")


def test_whitespace_handling():
    """Test handling of whitespace in expressions."""
    calc = CalculatorTool()

    # No spaces
    assert calc._execute_impl(expression="2+2") == "4"

    # Extra spaces
    assert calc._execute_impl(expression="  2  +  2  ") == "4"

    # Tabs and newlines (should be invalid)
    with pytest.raises(ValueError, match="Invalid characters in expression"):
        calc._execute_impl(expression="2 +\t2")
    with pytest.raises(ValueError, match="Invalid characters in expression"):
        calc._execute_impl(expression="2 +\n2")
