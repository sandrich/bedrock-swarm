"""Tests for the agency module."""

from typing import Any, Dict, Generator, List, Sequence, cast
from unittest.mock import MagicMock, patch

import pytest

from bedrock_swarm.agency.agency import Agency
from bedrock_swarm.agency.thread import Run, Thread
from bedrock_swarm.agents.base import BedrockAgent
from bedrock_swarm.config import AWSConfig
from bedrock_swarm.exceptions import InvalidModelError
from bedrock_swarm.memory.base import SimpleMemory
from bedrock_swarm.tools.base import BaseTool
from bedrock_swarm.tools.planning import PlanningTool
from bedrock_swarm.tools.send_message import SendMessageTool


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
        system_prompt="Test agent system prompt",
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
    assert isinstance(agency.shared_memory, SimpleMemory)
    assert agency.shared_instructions is None
    assert agency.event_system is not None


def test_agency_initialization_with_shared_memory() -> None:
    """Test agency initialization with shared memory and instructions."""
    shared_memory = SimpleMemory()
    shared_instructions = "Shared test instructions"

    agency = Agency(
        specialists=[],
        shared_memory=shared_memory,
        shared_instructions=shared_instructions,
    )

    assert agency.shared_memory == shared_memory
    assert agency.shared_instructions == shared_instructions


def test_coordinator_creation(agency: Agency, agent: BedrockAgent) -> None:
    """Test coordinator agent creation."""
    coordinator = agency.coordinator

    # Check basic properties
    assert coordinator.name == "coordinator"
    assert coordinator.model_id == "us.anthropic.claude-3-5-sonnet-20241022-v2:0"

    # Check tools
    assert len(coordinator.tools) == 2  # PlanningTool and SendMessageTool
    assert isinstance(coordinator.tools.get("create_plan"), PlanningTool)
    assert isinstance(coordinator.tools.get("SendMessage"), SendMessageTool)

    # Check system prompt
    assert coordinator.system_prompt is not None
    assert "AVAILABLE SPECIALISTS AND THEIR CAPABILITIES:" in coordinator.system_prompt
    assert agent.name in coordinator.system_prompt
    if agent.system_prompt:
        assert agent.system_prompt in coordinator.system_prompt


def test_communication_paths(agency: Agency, agent: BedrockAgent) -> None:
    """Test communication paths setup."""
    # Check coordinator paths
    assert "coordinator" in agency.communication_paths
    assert "user" in agency.communication_paths["coordinator"]
    assert agent.name in agency.communication_paths["coordinator"]

    # Check specialist paths
    assert agent.name in agency.communication_paths
    assert isinstance(agency.communication_paths[agent.name], list)


def test_setup_agent_communication(agency: Agency) -> None:
    """Test agent communication setup."""
    # Create a new agent to test communication setup
    agent = BedrockAgent(
        name="test_comm_agent",
        model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    )
    agency._setup_specialists([agent])

    # Set up communication paths before setting up communication
    agency.communication_paths[agent.name] = ["user"]
    agency._setup_agent_communication()

    # Check if agents have SendMessageTool
    assert any(isinstance(tool, SendMessageTool) for tool in agent.tools.values())


def test_create_thread_with_invalid_agent(agency: Agency) -> None:
    """Test creating a thread with invalid agent."""
    with pytest.raises(ValueError, match="Agent nonexistent not found"):
        agency.create_thread("nonexistent")


def test_get_thread_with_invalid_id(agency: Agency) -> None:
    """Test getting a thread with invalid ID."""
    assert agency.get_thread("nonexistent") is None


def test_get_completion_with_invalid_thread(
    agency: Agency, agent: BedrockAgent
) -> None:
    """Test getting a completion with invalid thread ID."""
    with pytest.raises(ValueError, match="Thread nonexistent not found"):
        agency.get_completion("Test message", thread_id="nonexistent")


def test_get_completion_with_no_agent(agency: Agency) -> None:
    """Test getting a completion with no agent in thread."""
    thread = Thread(None)  # Create thread with no agent
    agency.threads[thread.id] = thread

    with pytest.raises(ValueError, match=f"Thread {thread.id} has no agent assigned"):
        agency.get_completion("Test message", thread_id=thread.id)


def test_get_completion_with_shared_instructions(agent: BedrockAgent) -> None:
    """Test getting a completion with shared instructions."""
    shared_instructions = "Shared test instructions"
    agency = Agency(
        specialists=[agent],
        shared_instructions=shared_instructions,
    )

    response = agency.get_completion("Test message")
    assert isinstance(response, str)


def test_event_system_integration(agency: Agency, agent: BedrockAgent) -> None:
    """Test event system integration."""
    # Get completion to generate events
    agency.get_completion("Test message")

    # Check that events were created
    events = agency.event_system.get_events()
    assert len(events) > 0

    # Check event types and structure
    run_starts = agency.event_system.get_events(event_type="run_start")
    assert len(run_starts) > 0
    assert run_starts[0]["agent_name"] == agency.coordinator.name
    assert "message" in run_starts[0]["details"]


def test_add_agent(agency: Agency, agent: BedrockAgent) -> None:
    """Test adding an agent."""
    new_agent = BedrockAgent(
        name="new_test",
        model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    )
    agency._setup_specialists([new_agent])
    assert len(agency.agents) == 3  # Coordinator + 2 specialists
    assert agency.agents[new_agent.name] == new_agent
    assert new_agent.name in agency.communication_paths


def test_get_agent(agency: Agency, agent: BedrockAgent) -> None:
    """Test getting an agent."""
    assert agency.get_agent(agent.name) == agent


def test_create_thread(agency: Agency, agent: BedrockAgent) -> None:
    """Test creating a thread."""
    thread = agency.create_thread(agent.name)
    assert isinstance(thread, Thread)
    assert thread.agent == agent
    assert len(agency.threads) == 1
    assert thread.event_system == agency.event_system


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

    agency._setup_specialists([agent])
    # Set up communication paths before setting up communication
    agency.communication_paths[agent.name] = ["user"]
    agency._setup_agent_communication()  # Explicitly call to add SendMessageTool
    assert "new_test_agent" in agency.agents
    assert len(agent.tools) == 3  # 2 mock tools + SendMessageTool


def test_create_workflow(agency: Agency) -> None:
    """Test creating a workflow."""
    agent = BedrockAgent(
        name="new_test_agent",
        model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    )
    agency._setup_specialists([agent])
    response = agency.get_completion("Create a workflow")
    assert isinstance(response, str)


def test_execute_workflow(agency: Agency) -> None:
    """Test executing a workflow."""
    agent = BedrockAgent(
        name="new_test_agent",
        model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    )
    agency._setup_specialists([agent])
    response = agency.get_completion("Execute workflow")
    assert isinstance(response, str)


def test_get_run(agency: Agency, agent: BedrockAgent) -> None:
    """Test getting a run from a thread."""
    # Create thread and run
    thread = agency.create_thread(agent.name)
    agency.get_completion("Test message", thread_id=thread.id)

    # Get run
    run = agency.get_run(thread.id, thread.current_run.id)
    assert run is not None
    assert run.id == thread.current_run.id

    # Test nonexistent thread
    assert agency.get_run("nonexistent", "run_id") is None

    # Test nonexistent run
    assert agency.get_run(thread.id, "nonexistent") is None


def test_cancel_run(agency: Agency, agent: BedrockAgent) -> None:
    """Test cancelling a run."""
    # Create thread and run
    thread = agency.create_thread(agent.name)
    agency.threads[thread.id] = thread  # Make sure thread is in agency's threads dict

    # Create a run and set it to in_progress
    run = thread.current_run = Run()
    thread.runs.append(run)
    run.status = "in_progress"

    # Cancel run
    assert agency.cancel_run(thread.id, run.id)
    assert run.status == "failed"
    assert run.last_error == "Run cancelled by user"

    # Test nonexistent thread
    assert not agency.cancel_run("nonexistent", "run_id")

    # Test nonexistent run
    assert not agency.cancel_run(thread.id, "nonexistent")


def test_parse_agency_chart(agency: Agency) -> None:
    """Test parsing agency chart."""
    # Create test agents
    agent1 = BedrockAgent(
        name="agent1",
        model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    )
    agent2 = BedrockAgent(
        name="agent2",
        model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    )
    agent3 = BedrockAgent(
        name="agent3",
        model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    )

    # Test single agent
    agency._parse_agency_chart([agent1])
    assert "agent1" in agency.agents
    assert agency.communication_paths["agent1"] == ["user"]

    # Test agent pair
    agency._parse_agency_chart([[agent2, agent3]])
    assert "agent2" in agency.agents
    assert "agent3" in agency.agents
    assert "agent3" in agency.communication_paths["agent2"]


def test_get_event_trace(agency: Agency, agent: BedrockAgent) -> None:
    """Test getting event trace."""
    # Create some events
    thread = agency.create_thread(agent.name)

    # Mock the agent's generate method
    with patch.object(agent, "generate") as mock_generate:
        mock_generate.return_value = {"type": "message", "content": "Test response"}
        agency.get_completion("Test message", thread_id=thread.id)

        # Get trace
        trace = agency.get_event_trace()
        assert isinstance(trace, str)
        assert "run_start" in trace.lower()
        assert "run_complete" in trace.lower()
        assert "test response" in trace.lower()

        # Test with run_id filter
        filtered_trace = agency.get_event_trace(run_id=thread.current_run.id)
        assert "test response" in filtered_trace.lower()


def test_process_request(agency: Agency) -> None:
    """Test processing a request through planning and execution."""
    # Mock the coordinator's generate method to not create a plan first time
    mock_generate = MagicMock()
    mock_generate.side_effect = [
        {"type": "message", "content": "No plan"},  # First call - no plan
        {"type": "message", "content": "Plan created"},  # Second call - with plan
    ]

    # Mock execute_plan to avoid actual execution
    mock_execute = MagicMock(return_value={"1": "Test result"})

    with patch.object(agency.coordinator, "generate", mock_generate), patch.object(
        agency, "execute_plan", mock_execute
    ):
        # Make sure main thread is properly set up
        thread = agency.create_thread(agency.coordinator.name)
        agency.threads[thread.id] = thread
        agency.main_thread = thread

        # Test without plan creation first
        with pytest.raises(
            ValueError, match="Coordinator failed to create a valid plan"
        ):
            agency.process_request("Test request")

        # Now test with plan creation
        agency.current_plan = {
            "steps": [
                {
                    "step_number": 1,
                    "description": "Test step",
                    "specialist": "test",
                }
            ],
            "final_output_format": "Result: {output}",
        }
        response = agency.process_request("Test request")
        assert isinstance(response, str)


def test_execute_plan(agency: Agency, agent: BedrockAgent) -> None:
    """Test executing a plan."""
    # Create a test plan
    plan = {
        "steps": [
            {
                "step_number": 1,
                "description": "Test step 1",
                "specialist": agent.name,
            },
            {
                "step_number": 2,
                "description": "Test step 2",
                "specialist": agent.name,
                "requires_results_from": [1],
            },
        ],
        "final_output_format": "Results: {output}",
    }

    # Mock agent's generate method to return different responses for each step
    responses = [
        {"type": "message", "content": "Step 1 result"},
        {"type": "message", "content": "Step 2 result"},
    ]
    mock_generate = MagicMock(side_effect=responses)

    with patch.object(agent, "generate", mock_generate):
        # Create and set up main thread
        thread = agency.create_thread(agent.name)
        agency.threads[thread.id] = thread
        agency.main_thread = thread

        # Add agent to agency
        agency.agents[agent.name] = agent

        results = agency.execute_plan(plan)

        # Verify results
        assert len(results) == 2
        assert results["1"] == "Step 1 result"
        assert results["2"] == "Step 2 result"

        # Verify dependencies were handled
        calls = mock_generate.call_args_list
        assert len(calls) == 2
        assert (
            "Step 1 result" in calls[1][0][0]
        )  # Second call should include first step's result
