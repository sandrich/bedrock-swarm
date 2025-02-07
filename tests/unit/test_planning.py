"""Tests for planning tool implementation."""

import pytest

from bedrock_swarm.exceptions import ToolError
from bedrock_swarm.tools.planning import PlanningTool


@pytest.fixture
def planning_tool() -> PlanningTool:
    """Create a planning tool instance."""
    return PlanningTool()


def test_basic_plan_creation(planning_tool: PlanningTool) -> None:
    """Test creating a basic plan."""
    steps = [
        {
            "step_number": 1,
            "description": "Research the topic",
            "specialist": "researcher",
        },
        {
            "step_number": 2,
            "description": "Analyze findings",
            "specialist": "analyst",
        },
    ]
    result = planning_tool.execute(
        steps=steps, final_output_format="Summary: {findings}"
    )
    assert "Research the topic" in result
    assert "Analyze findings" in result
    assert "Summary: {findings}" in result


def test_plan_validation(planning_tool: PlanningTool) -> None:
    """Test plan validation."""
    # Test missing required fields
    invalid_steps = [
        {
            "step_number": 1,
            # Missing description
            "specialist": "researcher",
        }
    ]
    with pytest.raises(ToolError, match="Missing required parameter"):
        planning_tool.execute(
            steps=invalid_steps, final_output_format="Summary: {findings}"
        )

    # Test invalid step numbers
    invalid_steps = [
        {
            "step_number": 0,  # Should start from 1
            "description": "Research",
            "specialist": "researcher",
        }
    ]
    with pytest.raises(
        ToolError, match="Steps must be numbered sequentially starting from 1"
    ):
        planning_tool.execute(
            steps=invalid_steps, final_output_format="Summary: {findings}"
        )

    # Test non-sequential steps
    invalid_steps = [
        {
            "step_number": 1,
            "description": "Research",
            "specialist": "researcher",
        },
        {
            "step_number": 3,  # Skipped 2
            "description": "Analyze",
            "specialist": "analyst",
        },
    ]
    with pytest.raises(
        ToolError, match="Steps must be numbered sequentially starting from 1"
    ):
        planning_tool.execute(
            steps=invalid_steps, final_output_format="Summary: {findings}"
        )


def test_complex_plan(planning_tool: PlanningTool) -> None:
    """Test creating a complex plan with dependencies."""
    steps = [
        {
            "step_number": 1,
            "description": "Research market trends",
            "specialist": "researcher",
            "tools": ["search_tool", "data_analysis_tool"],
        },
        {
            "step_number": 2,
            "description": "Analyze competitor data",
            "specialist": "analyst",
            "requires": ["researcher"],
            "input_from": ["researcher"],
        },
        {
            "step_number": 3,
            "description": "Write report",
            "specialist": "writer",
            "requires": ["analyst"],
            "input_from": ["researcher", "analyst"],
        },
    ]
    result = planning_tool.execute(
        steps=steps, final_output_format="Executive Summary:\n{summary}"
    )
    assert "Research market trends" in result
    assert "Analyze competitor data" in result
    assert "Write report" in result
    assert "Executive Summary:\n{summary}" in result


def test_plan_with_custom_fields(planning_tool: PlanningTool) -> None:
    """Test creating a plan with custom fields."""
    steps = [
        {
            "step_number": 1,
            "description": "Research",
            "specialist": "researcher",
            "custom_field": "custom_value",
            "priority": "high",
        }
    ]
    result = planning_tool.execute(
        steps=steps, final_output_format="Summary: {findings}"
    )
    assert "Research" in result
    assert "researcher" in result


def test_empty_plan(planning_tool: PlanningTool) -> None:
    """Test handling of empty plan."""
    with pytest.raises(ToolError, match="Missing required parameter"):
        planning_tool.execute(steps=[])
