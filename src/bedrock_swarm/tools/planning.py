"""Tool for coordinator to create and validate execution plans."""

from typing import Any, Dict, List
import json

from ..tools.base import BaseTool


class PlanningTool(BaseTool):
    """Tool for creating and validating execution plans.
    
    This tool is specifically for the coordinator to:
    1. Break down a task into steps
    2. Identify which specialists are needed
    3. Determine the order of operations
    4. Get approval for the plan before execution
    """

    def __init__(self) -> None:
        """Initialize the planning tool."""
        self._name = "create_plan"
        self._description = "Create and validate a plan before executing any tasks"

    @property
    def name(self) -> str:
        """Get tool name."""
        return self._name

    @property
    def description(self) -> str:
        """Get tool description."""
        return self._description

    def get_schema(self) -> Dict[str, Any]:
        """Get JSON schema for the planning tool."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "steps": {
                        "type": "array",
                        "description": "List of steps in the plan",
                        "items": {
                            "type": "object",
                            "properties": {
                                "step_number": {"type": "integer"},
                                "description": {"type": "string"},
                                "specialist": {"type": "string"},
                                "requires_results_from": {
                                    "type": "array",
                                    "items": {"type": "integer"}
                                }
                            },
                            "required": ["step_number", "description", "specialist"]
                        }
                    },
                    "final_output_format": {
                        "type": "string",
                        "description": "Description of how the final result should be formatted"
                    }
                },
                "required": ["steps", "final_output_format"]
            }
        }

    def _execute_impl(self, *, steps: List[Dict[str, Any]], final_output_format: str, **kwargs: Any) -> str:
        """Execute the planning tool.

        Args:
            steps: List of steps in the plan
            final_output_format: Description of how the final result should be formatted

        Returns:
            String confirming the plan is valid and can proceed
        """

        # Validate steps are objects, not strings
        if any(isinstance(step, str) for step in steps):
            raise ValueError(
                "Steps must be objects with step_number, description, and specialist fields. "
                "Received array of strings instead. Example correct format:\n"
                '{"step_number": 1, "description": "Calculate X", "specialist": "calculator"}'
            )

        # Validate each step has required fields
        for step in steps:
            missing_fields = []
            for field in ["step_number", "description", "specialist"]:
                if field not in step:
                    missing_fields.append(field)
            if missing_fields:
                raise ValueError(
                    f"Step is missing required fields: {', '.join(missing_fields)}. "
                    "Each step must have step_number, description, and specialist fields."
                )

        # Validate steps are in order
        step_numbers = [step["step_number"] for step in steps]
        if step_numbers != list(range(1, len(steps) + 1)):
            raise ValueError(
                f"Steps must be numbered sequentially starting from 1. "
                f"Got step numbers: {step_numbers}"
            )

        # Validate dependencies
        for step in steps:
            if "requires_results_from" in step:
                for dep in step["requires_results_from"]:
                    if dep >= step["step_number"]:
                        raise ValueError(f"Step {step['step_number']} cannot depend on future step {dep}")
                    if dep not in step_numbers:
                        raise ValueError(f"Step {step['step_number']} depends on non-existent step {dep}")

        # Store the plan in the agency instance
        if "thread" in kwargs and hasattr(kwargs["thread"], "agent"):
            agency = kwargs["thread"].agent._agency
            if agency:
                agency.current_plan = {
                    "steps": steps,
                    "final_output_format": final_output_format
                }

        # Format the approved plan
        plan_output = ["Approved Plan:"]
        for step in steps:
            deps = f" (using results from steps {step['requires_results_from']})" if "requires_results_from" in step else ""
            plan_output.append(f"{step['step_number']}. {step['description']} → {step['specialist']}{deps}")
        plan_output.append(f"\nFinal Output Format: {final_output_format}")
        plan_output.append("\nPlan is approved. You can now proceed with execution.")

        return "\n".join(plan_output) 