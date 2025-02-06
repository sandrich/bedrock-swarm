"""Tests for the agency module."""

from typing import Dict
from unittest.mock import Mock, PropertyMock, patch

import pytest

from bedrock_swarm.agency.agency import Agency
from bedrock_swarm.agency.thread import ThreadMessage
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
        self._execute_mock = Mock(return_value="Tool result")

    @property
    def name(self) -> str:
        """Get tool name."""
        return self._name

    @property
    def description(self) -> str:
        """Get tool description."""
        return self._description

    def get_schema(self) -> Dict:
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
def aws_config() -> AWSConfig:
    """Create AWS config for testing."""
    return AWSConfig(region="us-west-2", profile="default")


@pytest.fixture
def agency(aws_config: AWSConfig) -> Agency:
    """Create agency for testing."""
    return Agency(
        aws_config=aws_config,
        shared_instructions="Shared instructions",
        shared_files=["file1.txt", "file2.txt"],
        temperature=0.8,
        max_tokens=2000,
    )


def test_agency_initialization(agency: Agency) -> None:
    """Test agency initialization."""
    assert agency.aws_config is not None
    assert agency.shared_instructions == "Shared instructions"
    assert agency.shared_files == ["file1.txt", "file2.txt"]
    assert agency.temperature == 0.8
    assert agency.max_tokens == 2000
    assert agency.agents == {}
    assert agency.threads == {}
    assert agency.agent_stats == {}
    assert agency.workflows == {}
    assert agency.active_workflows == {}
    assert agency.shared_state == {}


def test_create_thread(agency: Agency) -> None:
    """Test creating a thread."""
    # Create thread without agent
    thread = agency.create_thread()
    assert thread.thread_id in agency.threads
    assert thread.agent is None
    assert agency.agent_stats[thread.thread_id] == {"messages": 0, "tokens": 0}

    # Create thread with agent
    agent = agency.add_agent(
        name="test_agent",
        model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    )
    thread = agency.create_thread("test_agent")
    assert thread.thread_id in agency.threads
    assert thread.agent == agent


def test_get_thread(agency: Agency) -> None:
    """Test getting a thread."""
    thread = agency.create_thread()
    retrieved_thread = agency.get_thread(thread.thread_id)
    assert retrieved_thread == thread
    assert agency.get_thread("nonexistent") is None


def test_update_stats(agency: Agency) -> None:
    """Test updating thread statistics."""
    thread = agency.create_thread()
    agency._update_stats(thread.thread_id, 100)
    stats = agency.get_stats(thread.thread_id)
    assert stats["messages"] == 1
    assert stats["tokens"] == 100

    # Test nonexistent thread
    stats = agency.get_stats("nonexistent")
    assert stats == {}


def test_execute(agency: Agency) -> None:
    """Test executing a message in a thread."""
    # Create agent and thread
    agent = agency.add_agent(
        name="test_agent",
        model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    )
    thread = agency.create_thread("test_agent")

    # Mock agent's process_message and last_token_count
    agent.process_message = Mock(return_value="Test response")
    with patch(
        "bedrock_swarm.agents.base.BedrockAgent.last_token_count",
        new_callable=PropertyMock,
    ) as mock_token_count:
        mock_token_count.return_value = 50

        # Execute message
        response = agency.execute(thread.thread_id, "Test message")
        assert isinstance(response, ThreadMessage)
        assert response.content == "Test response"

        # Verify process_message was called correctly
        agent.process_message.assert_called_once_with("Test message", None)

        # Check stats were updated
        stats = agency.get_stats(thread.thread_id)
        assert stats["messages"] == 1
        assert stats["tokens"] == 50

    # Test nonexistent thread
    with pytest.raises(ValueError, match="Thread nonexistent does not exist"):
        agency.execute("nonexistent", "Test message")

    # Test thread without agent
    thread_without_agent = agency.create_thread()
    with pytest.raises(ValueError, match="Thread .* has no agent assigned"):
        agency.execute(thread_without_agent.thread_id, "Test message")


def test_add_agent(agency: Agency) -> None:
    """Test adding an agent."""
    tools = [MockTool()]
    agent = agency.add_agent(
        name="test_agent",
        model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        instructions="Test instructions",
        tools=tools,
        temperature=0.9,
        max_tokens=1500,
    )

    assert agent.name == "test_agent"
    assert agent.model_id == "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
    assert agent.instructions == "Test instructions"
    assert agent.temperature == 0.9
    assert agent.max_tokens == 1500
    assert len(agent.tools) == 1
    assert "test_agent" in agency.agents
    assert agency.agent_stats["test_agent"] == {"messages": 0, "tokens": 0}

    # Test duplicate agent
    with pytest.raises(ValueError):
        agency.add_agent(
            name="test_agent", model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0"
        )


def test_create_workflow(agency: Agency) -> None:
    """Test creating a workflow."""
    steps = [
        {
            "agent": "agent1",
            "instructions": "Step 1",
            "tools": [MockTool()],
            "input_from": [],
            "use_initial_input": True,
            "requires": [],
        },
        {
            "agent": "agent2",
            "instructions": "Step 2",
            "input_from": ["agent1"],
            "requires": ["agent1"],
        },
    ]

    workflow_id = agency.create_workflow("test_workflow", steps)
    assert workflow_id == "test_workflow"

    workflow = agency.get_workflow(workflow_id)
    assert workflow is not None
    assert workflow.name == "test_workflow"
    assert len(workflow.steps) == 2
    assert workflow.steps[0].agent == "agent1"
    assert workflow.steps[1].agent == "agent2"

    # Test duplicate workflow
    with pytest.raises(ValueError):
        agency.create_workflow("test_workflow", steps)


def test_get_workflow(agency: Agency) -> None:
    """Test getting a workflow."""
    steps = [{"agent": "agent1", "instructions": "Step 1"}]
    workflow_id = agency.create_workflow("test_workflow", steps)

    workflow = agency.get_workflow(workflow_id)
    assert workflow is not None
    assert workflow.name == "test_workflow"

    assert agency.get_workflow("nonexistent") is None
