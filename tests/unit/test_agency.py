"""Tests for the agency module."""

from typing import Any, Dict, Generator, List, Sequence, cast
from unittest.mock import MagicMock, Mock, PropertyMock, patch

import pytest

from bedrock_swarm.agency.agency import Agency
from bedrock_swarm.agency.thread import ThreadMessage
from bedrock_swarm.agents.base import BedrockAgent
from bedrock_swarm.config import AWSConfig
from bedrock_swarm.tools.base import BaseTool


class MockTool(BaseTool):
    """Mock tool for testing."""

    def __init__(
        self, name: str = "mock_tool", description: str = "Mock tool for testing"
    ) -> None:
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

    def _execute_impl(self, **kwargs: Any) -> str:
        """Execute the mock tool."""
        return cast(str, self._execute_mock(**kwargs))


@pytest.fixture
def aws_config() -> AWSConfig:
    """Create AWS config for testing."""
    return AWSConfig(region="us-west-2", profile="default")


@pytest.fixture
def mock_agent(aws_config: AWSConfig) -> Generator[BedrockAgent, None, None]:
    """Create a mock agent."""
    agent = BedrockAgent(
        name="test_agent",
        model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        aws_config=aws_config,
    )
    # Mock the process_message method
    mock_process = MagicMock(return_value="Test response")
    with patch.object(agent, "process_message", mock_process):
        yield agent


@pytest.fixture
def agency(aws_config: AWSConfig) -> Agency:
    """Create agency for testing."""
    return Agency(aws_config=aws_config)


def test_agency_initialization(agency: Agency) -> None:
    """Test agency initialization."""
    assert agency.aws_config is not None
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
    tools: Sequence[BaseTool] = [MockTool("tool1"), MockTool("tool2")]
    agent = agency.add_agent(
        name="test_agent",
        model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        tools=cast(List[BaseTool], tools),
    )
    assert agent.name == "test_agent"
    assert len(agent.tools) == 2
    assert "test_agent" in agency.agents


def test_add_agent_with_tools(agency: Agency) -> None:
    """Test adding an agent with tools."""
    tools: Sequence[BaseTool] = [MockTool("tool1"), MockTool("tool2")]
    agent = agency.add_agent(
        name="test_agent",
        model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        tools=cast(List[BaseTool], tools),
    )
    assert "test_agent" in agency.agents
    assert len(agent.tools) == 2


def test_get_agent(agency: Agency) -> None:
    """Test getting an agent."""
    agency.add_agent(
        name="test_agent",
        model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    )
    agent = agency.agents.get("test_agent")
    assert agent is not None
    assert agent.name == "test_agent"


def test_get_nonexistent_agent(agency: Agency) -> None:
    """Test getting a nonexistent agent."""
    agent = agency.agents.get("nonexistent")
    assert agent is None


def test_create_workflow(agency: Agency) -> None:
    """Test creating a workflow."""
    # Add an agent first
    agency.add_agent(
        name="test_agent",
        model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    )

    # Create workflow steps
    steps: List[Dict[str, Any]] = [
        {
            "agent": "test_agent",
            "instructions": "Test instructions",
            "use_initial_input": True,
        }
    ]

    workflow_id = agency.create_workflow("test_workflow", steps)
    workflow = agency.workflows[workflow_id]
    assert workflow.name == "test_workflow"
    assert len(workflow.steps) == 1
    assert workflow.steps[0].agent == "test_agent"
    assert workflow.steps[0].instructions == "Test instructions"
    assert workflow.steps[0].use_initial_input is True


def test_create_workflow_invalid_agent(agency: Agency) -> None:
    """Test creating a workflow with invalid agent."""
    steps: List[Dict[str, Any]] = [
        {
            "agent": "nonexistent",
            "instructions": "Test instructions",
        }
    ]

    # This should raise ValueError because the agent doesn't exist
    with pytest.raises(ValueError):
        agency.create_workflow("test_workflow", steps)


def test_execute_workflow(agency: Agency) -> None:
    """Test executing a workflow."""
    # Add an agent first
    agent = agency.add_agent(
        name="test_agent",
        model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    )

    # Create workflow steps
    steps: List[Dict[str, Any]] = [
        {
            "agent": "test_agent",
            "instructions": "Test instructions",
            "use_initial_input": True,
        }
    ]

    workflow = agency.create_workflow("test_workflow", steps)

    # Mock the process_message method
    mock_process = MagicMock(return_value="Test response")
    with patch.object(agent, "process_message", mock_process):
        results = agency.execute_workflow(workflow, {"input": "Test input"})
        assert "test_agent" in results
        assert results["test_agent"] == "Test response"
