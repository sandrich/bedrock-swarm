"""Tests for the workflow module."""

from typing import Any, Dict
from unittest.mock import MagicMock

import pytest

from bedrock_swarm.agency.workflow import Workflow, WorkflowStep
from bedrock_swarm.agents.base import BedrockAgent
from bedrock_swarm.config import AWSConfig
from bedrock_swarm.tools.base import BaseTool


class MockTool(BaseTool):
    """Mock tool for testing."""

    def __init__(
        self, name: str = "mock_tool", description: str = "Mock tool for testing"
    ):
        """Initialize mock tool."""
        self._name = name
        self._description = description
        self._execute_mock = MagicMock(return_value="Tool result")

    @property
    def name(self) -> str:
        """Get tool name."""
        return self._name

    @property
    def description(self) -> str:
        """Get tool description."""
        return self._description

    def get_schema(self) -> Dict[str, Any]:
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

    def _execute_impl(self, **kwargs) -> str:
        """Execute the mock tool."""
        return self._execute_mock(**kwargs)


@pytest.fixture
def aws_config():
    """Create AWS config for testing."""
    return AWSConfig(region="us-west-2", profile="default")


@pytest.fixture
def mock_agent(aws_config):
    """Create a mock agent."""
    agent = BedrockAgent(
        name="test_agent",
        model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        aws_config=aws_config,
    )
    agent.process_message = MagicMock(return_value="Test response")
    return agent


@pytest.fixture
def basic_workflow(aws_config):
    """Create basic workflow for testing."""
    return Workflow(
        name="test_workflow",
        steps=[
            WorkflowStep(
                agent="test_agent",
                instructions="Test instructions",
            )
        ],
    )


def test_workflow_step_creation():
    """Test WorkflowStep creation and defaults."""
    # Basic creation
    step = WorkflowStep(agent="test_agent")
    assert step.agent == "test_agent"
    assert step.instructions is None
    assert step.tools is None
    assert step.input_from is None
    assert step.use_initial_input is True
    assert step.requires is None

    # Full creation
    tools = [MockTool()]
    step = WorkflowStep(
        agent="test_agent",
        instructions="Test instructions",
        tools=tools,
        input_from=["agent1", "agent2"],
        use_initial_input=False,
        requires=["agent3"],
    )
    assert step.agent == "test_agent"
    assert step.instructions == "Test instructions"
    assert step.tools == tools
    assert step.input_from == ["agent1", "agent2"]
    assert step.use_initial_input is False
    assert step.requires == ["agent3"]


def test_workflow_validation():
    """Test workflow validation."""
    # Test duplicate agent names
    with pytest.raises(ValueError, match="Duplicate agent names"):
        Workflow(
            name="test",
            steps=[
                WorkflowStep(agent="agent1"),
                WorkflowStep(agent="agent1"),
            ],
        )

    # Test invalid input sources
    with pytest.raises(ValueError, match="Invalid input sources"):
        Workflow(
            name="test",
            steps=[
                WorkflowStep(agent="agent1"),
                WorkflowStep(agent="agent2", input_from=["agent3"]),
            ],
        )

    # Test invalid dependencies
    with pytest.raises(ValueError, match="Invalid dependencies"):
        Workflow(
            name="test",
            steps=[
                WorkflowStep(agent="agent1"),
                WorkflowStep(agent="agent2", requires=["agent3"]),
            ],
        )

    # Test circular dependencies
    with pytest.raises(ValueError, match="Circular dependency"):
        Workflow(
            name="test",
            steps=[
                WorkflowStep(agent="agent1", requires=["agent2"]),
                WorkflowStep(agent="agent2", requires=["agent1"]),
            ],
        )


def test_workflow_execution_plan():
    """Test workflow execution plan generation."""
    workflow = Workflow(
        name="test",
        steps=[
            WorkflowStep(agent="agent3", requires=["agent1", "agent2"]),
            WorkflowStep(agent="agent1"),
            WorkflowStep(agent="agent2", requires=["agent1"]),
            WorkflowStep(agent="agent4", input_from=["agent2", "agent3"]),
        ],
    )

    plan = workflow.get_execution_plan()

    # Verify order respects dependencies
    agent_order = [step.agent for step in plan]
    assert agent_order.index("agent1") < agent_order.index("agent2")
    assert agent_order.index("agent2") < agent_order.index("agent3")
    assert agent_order.index("agent3") < agent_order.index("agent4")


def test_workflow_serialization():
    """Test workflow serialization/deserialization."""
    tools = [MockTool("tool1"), MockTool("tool2")]
    original = Workflow(
        name="test",
        steps=[
            WorkflowStep(
                agent="agent1",
                instructions="Step 1",
                tools=tools,
                use_initial_input=True,
            ),
            WorkflowStep(
                agent="agent2",
                instructions="Step 2",
                input_from=["agent1"],
                requires=["agent1"],
                use_initial_input=False,
            ),
        ],
    )

    # Convert to dict
    data = original.to_dict()

    # Verify dict structure
    assert data["name"] == "test"
    assert len(data["steps"]) == 2
    assert data["steps"][0]["agent"] == "agent1"
    assert data["steps"][0]["instructions"] == "Step 1"
    assert data["steps"][0]["tools"] == ["MockTool", "MockTool"]
    assert data["steps"][0]["use_initial_input"] is True

    assert data["steps"][1]["agent"] == "agent2"
    assert data["steps"][1]["instructions"] == "Step 2"
    assert data["steps"][1]["input_from"] == ["agent1"]
    assert data["steps"][1]["requires"] == ["agent1"]
    assert data["steps"][1]["use_initial_input"] is False

    # Convert back to workflow
    reconstructed = Workflow.from_dict(data)
    assert reconstructed.name == original.name
    assert len(reconstructed.steps) == len(original.steps)

    # Compare steps
    for orig_step, recon_step in zip(original.steps, reconstructed.steps):
        assert orig_step.agent == recon_step.agent
        assert orig_step.instructions == recon_step.instructions
        assert orig_step.input_from == recon_step.input_from
        assert orig_step.requires == recon_step.requires
        assert orig_step.use_initial_input == recon_step.use_initial_input


def test_complex_workflow_execution(aws_config):
    """Test execution of a complex workflow with dependencies and tools."""
    # Create agents
    agents = {
        "researcher": BedrockAgent(
            name="researcher",
            model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
            aws_config=aws_config,
        ),
        "analyst": BedrockAgent(
            name="analyst",
            model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
            aws_config=aws_config,
        ),
        "writer": BedrockAgent(
            name="writer",
            model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
            aws_config=aws_config,
        ),
    }

    # Mock responses
    agents["researcher"].process_message = MagicMock(return_value="Research findings")
    agents["analyst"].process_message = MagicMock(return_value="Analysis results")
    agents["writer"].process_message = MagicMock(return_value="Final report")

    # Create workflow
    workflow = Workflow(
        name="research_workflow",
        steps=[
            WorkflowStep(
                agent="researcher",
                instructions="Research the topic",
                tools=[MockTool("search_tool")],
            ),
            WorkflowStep(
                agent="analyst",
                instructions="Analyze the research",
                input_from=["researcher"],
                requires=["researcher"],
            ),
            WorkflowStep(
                agent="writer",
                instructions="Write report",
                input_from=["researcher", "analyst"],
                requires=["analyst"],
            ),
        ],
    )

    # Add agents to workflow
    workflow.agents = agents

    # Execute workflow
    results = workflow.execute({"input": "Research AI advancements"})

    # Verify results
    assert results["researcher"] == "Research findings"
    assert results["analyst"] == "Analysis results"
    assert results["writer"] == "Final report"

    # Print actual messages for debugging
    print("\nActual messages:")
    for call in agents["researcher"].process_message.call_args_list:
        print("Researcher:", repr(call[0][0]))
    for call in agents["analyst"].process_message.call_args_list:
        print("Analyst:", repr(call[0][0]))
    for call in agents["writer"].process_message.call_args_list:
        print("Writer:", repr(call[0][0]))

    # Verify message passing
    agents["researcher"].process_message.assert_called_once_with(
        "Research the topic\n\nInput: Research AI advancements",
        workflow.get_step("researcher").tools,
    )

    agents["analyst"].process_message.assert_called_once_with(
        "Analyze the research\n\nInput: Research AI advancements\n\nresearcher result: Research findings",
        None,
    )

    agents["writer"].process_message.assert_called_once_with(
        "Write report\n\nInput: Research AI advancements\n\nresearcher result: Research findings\n\nanalyst result: Analysis results",
        None,
    )


def test_workflow_step_management(basic_workflow):
    """Test step management operations."""
    # Add step
    new_step = WorkflowStep(
        agent="agent2",
        instructions="Step 2",
        requires=["test_agent"],
    )
    basic_workflow.add_step(new_step)
    assert len(basic_workflow.steps) == 2

    # Get step
    step = basic_workflow.get_step("agent2")
    assert step is not None
    assert step.agent == "agent2"
    assert step.instructions == "Step 2"

    # Remove step
    assert basic_workflow.remove_step("agent2")
    assert len(basic_workflow.steps) == 1
    assert basic_workflow.get_step("agent2") is None

    # Remove nonexistent step
    assert not basic_workflow.remove_step("nonexistent")

    # Clear steps
    basic_workflow.steps.clear()
    assert len(basic_workflow.steps) == 0
