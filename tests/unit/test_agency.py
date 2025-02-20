"""Tests for agency implementation."""

from unittest.mock import MagicMock, patch

import pytest

from bedrock_swarm.agency.agency import Agency
from bedrock_swarm.agents.base import BedrockAgent
from bedrock_swarm.events import EventSystem
from bedrock_swarm.memory.base import SimpleMemory
from bedrock_swarm.tools.send_message import SendMessageTool


@pytest.fixture
def mock_agent():
    """Create a mock agent."""
    agent = MagicMock(spec=BedrockAgent)
    agent.name = "test_agent"
    agent.tools = {}
    return agent


@pytest.fixture
def mock_thread():
    """Create a mock thread."""
    thread = MagicMock()
    thread.process_message.return_value = "Test response"
    return thread


@pytest.fixture
def agency(mock_agent):
    """Create an agency with a mock agent."""
    with patch("bedrock_swarm.agency.agency.Thread") as mock_thread_class:
        mock_thread_class.return_value = MagicMock()
        return Agency(agents={"test_agent": mock_agent})


def test_agency_initialization(mock_agent):
    """Test agency initialization."""
    # Test with default memory
    agency = Agency(agents={"test_agent": mock_agent})
    assert isinstance(agency.shared_memory, SimpleMemory)
    assert agency.agents == {"test_agent": mock_agent}
    assert isinstance(agency.event_system, EventSystem)
    assert isinstance(agency.threads, dict)

    # Test with custom memory
    custom_memory = SimpleMemory()
    agency = Agency(agents={"test_agent": mock_agent}, shared_memory=custom_memory)
    assert agency.shared_memory is custom_memory


def test_setup_agent_communication(agency, mock_agent):
    """Test setting up inter-agent communication."""
    # Add another agent
    second_agent = MagicMock(spec=BedrockAgent)
    second_agent.name = "second_agent"
    second_agent.tools = {}
    agency.add_agent(second_agent)

    # Verify SendMessageTool was added to both agents
    assert "send_message" in mock_agent.tools
    assert "send_message" in second_agent.tools

    # Verify valid recipients
    tool1 = mock_agent.tools["send_message"]
    tool2 = second_agent.tools["send_message"]
    assert tool1._valid_recipients == ["second_agent"]
    assert tool2._valid_recipients == ["test_agent"]


def test_get_agent(agency, mock_agent):
    """Test getting agents by name."""
    # Test getting existing agent
    assert agency.get_agent("test_agent") is mock_agent

    # Test getting non-existent agent
    with pytest.raises(KeyError, match="Agent 'non_existent' not found"):
        agency.get_agent("non_existent")


def test_get_completion(agency, mock_agent):
    """Test getting completions from agents."""
    with patch("bedrock_swarm.agency.agency.Thread") as mock_thread_class:
        mock_thread = MagicMock()
        mock_thread.process_message.return_value = "Test response"
        mock_thread_class.return_value = mock_thread

        # Test getting completion
        response = agency.get_completion(
            message="Test message",
            recipient_agent=mock_agent,
            thread_id="test_thread",
        )

        # Verify response
        assert response == "Test response"

        # Verify thread creation and usage
        thread_id = "test_agent_test_thread"
        assert thread_id in agency.threads
        agency.threads[thread_id].process_message.assert_called_once_with(
            "Test message"
        )


def test_process_request(agency, mock_agent):
    """Test processing requests through agents."""
    with patch("bedrock_swarm.agency.agency.Thread") as mock_thread_class:
        mock_thread = MagicMock()
        mock_thread.process_message.return_value = "Test response"
        mock_thread_class.return_value = mock_thread

        # Test processing request
        response = agency.process_request(
            message="Test message",
            agent_name="test_agent",
        )

        # Verify response
        assert response == "Test response"

        # Verify thread creation and usage
        thread_id = "test_agent_thread"
        assert thread_id in agency.threads
        agency.threads[thread_id].process_message.assert_called_once_with(
            "Test message"
        )

        # Test with non-existent agent
        with pytest.raises(KeyError, match="Agent 'non_existent' not found"):
            agency.process_request("Test message", "non_existent")


def test_add_agent(agency, mock_agent):
    """Test adding new agents."""
    # Create new agent
    new_agent = MagicMock(spec=BedrockAgent)
    new_agent.name = "new_agent"
    new_agent.tools = {}

    # Add agent
    agency.add_agent(new_agent)

    # Verify agent was added
    assert "new_agent" in agency.agents
    assert agency.agents["new_agent"] is new_agent

    # Verify communication tools were updated
    assert "send_message" in new_agent.tools
    assert "send_message" in mock_agent.tools
    assert isinstance(new_agent.tools["send_message"], SendMessageTool)
    assert isinstance(mock_agent.tools["send_message"], SendMessageTool)

    # Verify valid recipients were updated
    assert mock_agent.tools["send_message"]._valid_recipients == ["new_agent"]
    assert new_agent.tools["send_message"]._valid_recipients == ["test_agent"]


def test_get_memory(agency):
    """Test getting shared memory."""
    memory = agency.get_memory()
    assert isinstance(memory, SimpleMemory)
    assert memory is agency.shared_memory


def test_thread_reuse(agency, mock_agent):
    """Test that threads are reused for the same agent/thread combination."""
    with patch("bedrock_swarm.agency.agency.Thread") as mock_thread_class:
        mock_thread = MagicMock()
        mock_thread.process_message.return_value = "Test response"
        mock_thread_class.return_value = mock_thread

        # Make two requests with same thread ID
        agency.get_completion("Message 1", mock_agent, "thread1")
        agency.get_completion("Message 2", mock_agent, "thread1")

        # Verify thread was created only once
        assert mock_thread_class.call_count == 1
        assert len(agency.threads) == 1

        # Verify both messages were processed
        thread = agency.threads["test_agent_thread1"]
        assert thread.process_message.call_count == 2
        thread.process_message.assert_any_call("Message 1")
        thread.process_message.assert_any_call("Message 2")


def test_event_system_propagation(agency, mock_agent):
    """Test that event system is properly propagated to threads."""
    with patch("bedrock_swarm.agency.agency.Thread") as mock_thread_class:
        mock_thread = MagicMock()
        mock_thread_class.return_value = mock_thread

        # Create thread through request
        agency.process_request("Test message", "test_agent")

        # Verify event system was set
        assert mock_thread.event_system is agency.event_system
