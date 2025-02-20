"""Tests for send message tool implementation."""

from unittest.mock import MagicMock

import pytest

from bedrock_swarm.tools.send_message import SendMessageTool


@pytest.fixture
def mock_agency():
    """Create a mock agency."""
    agency = MagicMock()
    agency.get_agent.return_value = MagicMock()
    agency.get_completion.return_value = "Response from recipient"
    return agency


@pytest.fixture
def mock_thread():
    """Create a mock thread."""
    thread = MagicMock()
    thread.id = "test_thread_id"
    return thread


@pytest.fixture
def send_message_tool(mock_agency):
    """Create a send message tool instance."""
    return SendMessageTool(
        valid_recipients=["agent1", "agent2"],
        description="Test send message tool",
        agency=mock_agency,
    )


def test_initialization():
    """Test send message tool initialization."""
    # Test with all parameters
    tool = SendMessageTool(
        valid_recipients=["agent1", "agent2"],
        description="Custom description",
        agency=MagicMock(),
    )
    assert tool.name == "SendMessage"
    assert tool.description == "Custom description"
    assert tool._valid_recipients == ["agent1", "agent2"]
    assert tool._agency is not None

    # Test with minimal parameters
    tool = SendMessageTool()
    assert tool.name == "SendMessage"
    assert tool.description == "Send a message to another agent"
    assert tool._valid_recipients == []
    assert tool._agency is None


def test_schema(send_message_tool):
    """Test send message tool schema."""
    schema = send_message_tool.get_schema()

    assert schema["name"] == "SendMessage"
    assert schema["description"] == "Test send message tool"
    assert "parameters" in schema
    assert schema["parameters"]["type"] == "object"

    properties = schema["parameters"]["properties"]
    assert "recipient" in properties
    assert "message" in properties
    assert schema["parameters"]["required"] == ["recipient", "message"]

    # Verify recipient description includes valid recipients
    assert "agent1" in properties["recipient"]["description"]
    assert "agent2" in properties["recipient"]["description"]


def test_successful_message_send(send_message_tool, mock_thread, mock_agency):
    """Test successful message sending."""
    response = send_message_tool._execute_impl(
        recipient="agent1",
        message="Test message",
        thread=mock_thread,
    )

    assert response == "Response from recipient"
    mock_agency.get_agent.assert_called_once_with("agent1")
    mock_agency.get_completion.assert_called_once_with(
        message="Test message",
        recipient_agent=mock_agency.get_agent.return_value,
        thread_id="test_thread_id",
    )


def test_invalid_recipient(send_message_tool, mock_thread):
    """Test sending message to invalid recipient."""
    with pytest.raises(ValueError, match="Invalid recipient: invalid_agent"):
        send_message_tool._execute_impl(
            recipient="invalid_agent",
            message="Test message",
            thread=mock_thread,
        )


def test_missing_thread(send_message_tool):
    """Test sending message without thread."""
    with pytest.raises(ValueError, match="No thread provided"):
        send_message_tool._execute_impl(
            recipient="agent1",
            message="Test message",
        )


def test_missing_recipient_agent(send_message_tool, mock_thread):
    """Test behavior when recipient agent is not found."""
    # Make get_agent return None to simulate missing agent
    send_message_tool._agency.get_agent.return_value = None

    with pytest.raises(ValueError, match="Recipient agent agent1 not found"):
        send_message_tool._execute_impl(
            recipient="agent1",
            message="Test message",
            thread=mock_thread,
        )


def test_no_agency(mock_thread):
    """Test sending message without agency configured."""
    tool = SendMessageTool(valid_recipients=["agent1"])

    with pytest.raises(ValueError, match="No thread provided"):
        tool._execute_impl(
            recipient="agent1",
            message="Test message",
        )


def test_empty_valid_recipients():
    """Test schema generation with no valid recipients."""
    tool = SendMessageTool()
    schema = tool.get_schema()

    assert (
        "Valid recipients:"
        in schema["parameters"]["properties"]["recipient"]["description"]
    )
