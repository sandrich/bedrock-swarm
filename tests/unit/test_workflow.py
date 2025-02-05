"""Tests for the workflow module."""

from unittest.mock import MagicMock, patch

import pytest

from bedrock_swarm.agents.base import BedrockAgent
from bedrock_swarm.config import AWSConfig
from bedrock_swarm.tools.base import BaseTool
from bedrock_swarm.workflow.workflow import Workflow


class MockTool(BaseTool):
    """Mock tool for testing."""

    def __init__(self, name="mock_tool"):
        """Initialize mock tool."""
        super().__init__(name=name)
        self._execute_mock = MagicMock(return_value="Tool result")

    def execute(self, **kwargs):
        """Execute the tool."""
        return self._execute_mock(**kwargs)

    def get_schema(self):
        """Get tool schema."""
        return {
            "name": self.name,
            "description": "Mock tool for testing",
            "parameters": {
                "type": "object",
                "properties": {
                    "param1": {"type": "string"},
                    "param2": {"type": "integer"},
                },
                "required": ["param1"],
            },
        }


@pytest.fixture
def aws_config():
    """Create AWS config for testing."""
    return AWSConfig(region="us-west-2", profile="default")


@pytest.fixture
def workflow(aws_config):
    """Create workflow for testing."""
    return Workflow(
        name="test_workflow",
        steps=[
            {
                "agent": "test_agent",
                "instructions": "Test instructions",
            }
        ],
        aws_config=aws_config,
    )


def test_workflow_initialization(workflow):
    """Test workflow initialization."""
    assert workflow.name == "test_workflow"
    assert len(workflow.steps) == 1
    assert workflow.steps[0]["agent"] == "test_agent"
    assert workflow.steps[0]["instructions"] == "Test instructions"


def test_add_step(workflow):
    """Test adding a step."""
    workflow.add_step(
        agent="new_agent",
        instructions="New instructions",
    )
    assert len(workflow.steps) == 2
    assert workflow.steps[1]["agent"] == "new_agent"
    assert workflow.steps[1]["instructions"] == "New instructions"


def test_remove_step(workflow):
    """Test removing a step."""
    workflow.add_step(
        agent="new_agent",
        instructions="New instructions",
    )
    workflow.remove_step(0)
    assert len(workflow.steps) == 1
    assert workflow.steps[0]["agent"] == "new_agent"


def test_remove_nonexistent_step(workflow):
    """Test removing a nonexistent step."""
    with pytest.raises(IndexError):
        workflow.remove_step(1)


def test_clear_steps(workflow):
    """Test clearing all steps."""
    workflow.add_step(
        agent="new_agent",
        instructions="New instructions",
    )
    workflow.clear_steps()
    assert len(workflow.steps) == 0


def test_execute_workflow(workflow):
    """Test executing a workflow."""
    agent = BedrockAgent(
        name="test_agent",
        model_id="anthropic.claude-v2",
        aws_config=workflow.aws_config,
    )
    agent.process_message = MagicMock(return_value="Test response")

    with patch.dict(workflow.agents, {"test_agent": agent}):
        results = workflow.execute({"input": "Test input"})
        assert results["test_agent"] == "Test response"
        agent.process_message.assert_called_once_with(
            "Test instructions\n\nInput: Test input",
            None,
        )


def test_execute_workflow_with_tool(workflow):
    """Test executing a workflow with a tool."""
    agent = BedrockAgent(
        name="test_agent",
        model_id="anthropic.claude-v2",
        aws_config=workflow.aws_config,
    )
    tool = MockTool()
    agent.add_tool(tool)
    agent.process_message = MagicMock(return_value="Test response with tool")

    with patch.dict(workflow.agents, {"test_agent": agent}):
        results = workflow.execute({"input": "Test input"})
        assert results["test_agent"] == "Test response with tool"
        agent.process_message.assert_called_once_with(
            "Test instructions\n\nInput: Test input",
            None,
        )


def test_execute_workflow_with_multiple_steps(workflow):
    """Test executing a workflow with multiple steps."""
    workflow.add_step(
        agent="agent2",
        instructions="Step 2 instructions",
    )

    agent1 = BedrockAgent(
        name="test_agent",
        model_id="anthropic.claude-v2",
        aws_config=workflow.aws_config,
    )
    agent2 = BedrockAgent(
        name="agent2",
        model_id="anthropic.claude-v2",
        aws_config=workflow.aws_config,
    )

    agent1.process_message = MagicMock(return_value="Response 1")
    agent2.process_message = MagicMock(return_value="Response 2")

    with patch.dict(
        workflow.agents,
        {
            "test_agent": agent1,
            "agent2": agent2,
        },
    ):
        results = workflow.execute({"input": "Test input"})
        assert results["test_agent"] == "Response 1"
        assert results["agent2"] == "Response 2"
        agent1.process_message.assert_called_once_with(
            "Test instructions\n\nInput: Test input",
            None,
        )
        agent2.process_message.assert_called_once_with(
            "Step 2 instructions\n\nInput: Test input\nStep 1 result: Response 1",
            None,
        )
