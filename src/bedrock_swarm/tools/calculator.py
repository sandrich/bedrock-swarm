"""Calculator tool for basic arithmetic."""

from typing import Any, Dict

from .base import BaseTool


class CalculatorTool(BaseTool):
    """Simple calculator tool for basic arithmetic."""

    def __init__(
        self,
        name: str = "calculator",
        description: str = "Perform basic arithmetic calculations",
    ) -> None:
        """Initialize the calculator tool.

        Args:
            name: Name of the tool
            description: Description of the tool
        """
        self._name = name
        self._description = description

    @property
    def name(self) -> str:
        """Get tool name."""
        return self._name

    @property
    def description(self) -> str:
        """Get tool description."""
        return self._description

    def get_schema(self) -> Dict[str, Any]:
        """Get JSON schema for the calculator tool."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Arithmetic expression to evaluate (e.g. '2 + 2' or '5 * 3')",
                    }
                },
                "required": ["expression"],
            },
        }

    def _execute_impl(self, *, expression: str, **kwargs: Any) -> str:
        """Execute the calculator.

        Args:
            expression: Arithmetic expression to evaluate

        Returns:
            Result of the calculation

        Raises:
            ValueError: If expression is invalid
        """
        # Only allow basic arithmetic for safety
        allowed = set("0123456789+-*/(). ")
        if not all(c in allowed for c in expression):
            raise ValueError("Invalid characters in expression")

        try:
            # Evaluate the expression safely
            result = eval(expression, {"__builtins__": {}})
            return str(result)
        except Exception as e:
            raise ValueError(f"Invalid expression: {str(e)}")
