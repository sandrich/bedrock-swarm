"""Tests for the agency module."""

from typing import Any, Dict, Generator, List, Sequence, cast
from unittest.mock import MagicMock, patch

import pytest

from bedrock_swarm.agency.agency import Agency
from bedrock_swarm.agency.thread import Thread
from bedrock_swarm.agents.base import BedrockAgent
from bedrock_swarm.config import AWSConfig
from bedrock_swarm.exceptions import InvalidModelError
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
def mock_agent() -> Generator[BedrockAgent, None, None]:
    """Create a mock agent."""
    agent = BedrockAgent(
        name="test_agent",
        model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    )
    # Mock the process_message method
    mock_process = MagicMock(return_value="Test response")
    with patch.object(agent, "process_message", mock_process):
        yield agent


@pytest.fixture
def mock_model() -> MagicMock:
    """Create a mock model."""
    mock = MagicMock()
    mock.invoke.return_value = {"content": "Test response"}
    return mock


@pytest.fixture
def agent(mock_model: MagicMock) -> BedrockAgent:
    """Create a test agent."""
    with patch("bedrock_swarm.models.factory.ModelFactory.create_model") as mock_create:
        mock_create.return_value = mock_model
        return BedrockAgent(
            name="test",
            model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        )


@pytest.fixture
def agency(agent: BedrockAgent) -> Agency:
    """Create a test agency."""
    agency = Agency(specialists=[agent])
    agency.threads.clear()  # Clear any threads created during initialization
    return agency


def test_agency_initialization(agency: Agency) -> None:
    """Test agency initialization."""
    assert len(agency.agents) == 2  # Coordinator + 1 specialist
    assert len(agency.threads) == 0


def test_add_agent(agency: Agency, agent: BedrockAgent) -> None:
    """Test adding an agent."""
    new_agent = BedrockAgent(
        name="new_test",
        model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    )
    agency.add_agent(new_agent)
    assert len(agency.agents) == 3  # Coordinator + 2 specialists
    assert agency.agents[new_agent.name] == new_agent


def test_get_agent(agency: Agency, agent: BedrockAgent) -> None:
    """Test getting an agent."""
    assert agency.get_agent(agent.name) == agent


def test_create_thread(agency: Agency, agent: BedrockAgent) -> None:
    """Test creating a thread."""
    thread = agency.create_thread(agent.name)
    assert isinstance(thread, Thread)
    assert thread.agent == agent
    assert len(agency.threads) == 1


def test_get_thread(agency: Agency, agent: BedrockAgent) -> None:
    """Test getting a thread."""
    thread = agency.create_thread(agent.name)
    assert agency.get_thread(thread.id) == thread


def test_get_completion(agency: Agency, agent: BedrockAgent) -> None:
    """Test getting a completion."""
    response = agency.get_completion("Test message", recipient_agent=agent)
    assert response == "Test response"


def test_create_workflow_invalid_agent(agency: Agency) -> None:
    """Test creating a workflow with invalid agent."""
    # Get completion with nonexistent agent
    with pytest.raises(InvalidModelError, match="Unsupported model family"):
        agency.get_completion(
            "Test message",
            recipient_agent=BedrockAgent(
                name="nonexistent",
                model_id="test.model",
            ),
        )


def test_execute(agency: Agency) -> None:
    """Test executing a message in a thread."""
    # Create thread
    response = agency.get_completion("Test message")
    assert isinstance(response, str)


def test_add_agent_with_tools(agency: Agency) -> None:
    """Test adding an agent with tools."""
    tools: Sequence[BaseTool] = [MockTool("tool1"), MockTool("tool2")]
    agent = BedrockAgent(
        name="new_test_agent",
        model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        tools=cast(List[BaseTool], tools),
    )

    # Add agent through _setup_specialists
    agency._setup_specialists([agent])
    assert "new_test_agent" in agency.agents
    assert len(agent.tools) == 2


def test_create_workflow(agency: Agency) -> None:
    """Test creating a workflow."""
    # Add an agent first
    agent = BedrockAgent(
        name="new_test_agent",
        model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    )
    agency._setup_specialists([agent])

    # Get completion to simulate workflow creation
    response = agency.get_completion("Create a workflow")
    assert isinstance(response, str)


def test_execute_workflow(agency: Agency) -> None:
    """Test executing a workflow."""
    # Add an agent first
    agent = BedrockAgent(
        name="new_test_agent",
        model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    )
    agency._setup_specialists([agent])

    # Get completion to simulate workflow execution
    response = agency.get_completion("Execute workflow")
    assert isinstance(response, str)
