"""Tests for the event system."""

from typing import Dict

import pytest

from bedrock_swarm.events import EventSystem


@pytest.fixture
def event_system() -> EventSystem:
    """Create an event system for testing."""
    return EventSystem()


@pytest.fixture
def sample_event() -> Dict[str, str]:
    """Create sample event parameters."""
    return {
        "type": "message_sent",
        "agent_name": "test_agent",
        "run_id": "test_run",
        "thread_id": "test_thread",
        "details": {"message": "Test message"},
        "metadata": {"key": "value"},
    }


def test_create_event(event_system: EventSystem, sample_event: Dict[str, str]) -> None:
    """Test event creation."""
    event_id = event_system.create_event(**sample_event)

    assert len(event_system.events) == 1
    event = event_system.events[0]

    assert event["id"] == event_id
    assert event["type"] == sample_event["type"]
    assert event["agent_name"] == sample_event["agent_name"]
    assert event["run_id"] == sample_event["run_id"]
    assert event["thread_id"] == sample_event["thread_id"]
    assert event["details"] == sample_event["details"]
    assert event["metadata"] == sample_event["metadata"]
    assert event["parent_event_id"] is None
    assert isinstance(event["timestamp"], str)


def test_event_scope(event_system: EventSystem, sample_event: Dict[str, str]) -> None:
    """Test event scope management."""
    # Create parent event
    parent_id = event_system.create_event(**sample_event)

    # Start scope
    event_system.start_event_scope(parent_id)

    # Create child event
    event_system.create_event(**sample_event)

    # End scope
    event_system.end_event_scope()

    # Create sibling event
    event_system.create_event(**sample_event)

    # Verify relationships
    assert event_system.events[1]["parent_event_id"] == parent_id  # Child has parent
    assert event_system.events[2]["parent_event_id"] is None  # Sibling has no parent


def test_get_events_filtering(event_system: EventSystem) -> None:
    """Test event filtering."""
    # Create events with different attributes
    event_system.create_event(
        type="message_sent",
        agent_name="agent1",
        run_id="run1",
        thread_id="thread1",
        details={},
    )
    event_system.create_event(
        type="tool_start",
        agent_name="agent1",
        run_id="run1",
        thread_id="thread2",
        details={},
    )
    event_system.create_event(
        type="message_sent",
        agent_name="agent2",
        run_id="run2",
        thread_id="thread1",
        details={},
    )

    # Test filtering by run_id
    run1_events = event_system.get_events(run_id="run1")
    assert len(run1_events) == 2
    assert all(e["run_id"] == "run1" for e in run1_events)

    # Test filtering by thread_id
    thread1_events = event_system.get_events(thread_id="thread1")
    assert len(thread1_events) == 2
    assert all(e["thread_id"] == "thread1" for e in thread1_events)

    # Test filtering by agent_name
    agent1_events = event_system.get_events(agent_name="agent1")
    assert len(agent1_events) == 2
    assert all(e["agent_name"] == "agent1" for e in agent1_events)

    # Test filtering by event_type
    message_events = event_system.get_events(event_type="message_sent")
    assert len(message_events) == 2
    assert all(e["type"] == "message_sent" for e in message_events)

    # Test multiple filters
    filtered = event_system.get_events(
        run_id="run1",
        agent_name="agent1",
        event_type="message_sent",
    )
    assert len(filtered) == 1
    assert filtered[0]["run_id"] == "run1"
    assert filtered[0]["agent_name"] == "agent1"
    assert filtered[0]["type"] == "message_sent"


def test_get_event_chain(
    event_system: EventSystem, sample_event: Dict[str, str]
) -> None:
    """Test event chain retrieval."""
    # Create a chain of events
    root_id = event_system.create_event(**sample_event)

    event_system.start_event_scope(root_id)
    child1_id = event_system.create_event(**sample_event)

    event_system.start_event_scope(child1_id)
    child2_id = event_system.create_event(**sample_event)

    # Get chain from leaf node
    chain = event_system.get_event_chain(child2_id)

    assert len(chain) == 3
    assert chain[0]["id"] == root_id
    assert chain[1]["id"] == child1_id
    assert chain[2]["id"] == child2_id


def test_format_event(event_system: EventSystem, sample_event: Dict[str, str]) -> None:
    """Test event formatting."""
    event_system.create_event(**sample_event)
    formatted = event_system.format_event(event_system.events[0])

    # Check basic formatting
    assert "MESSAGE_SENT" in formatted
    assert "test_agent" in formatted
    assert "Test message" in formatted
    assert "Metadata" in formatted
    assert "key: value" in formatted


def test_format_event_chain(
    event_system: EventSystem, sample_event: Dict[str, str]
) -> None:
    """Test event chain formatting."""
    # Create events
    root_id = event_system.create_event(**sample_event)
    event_system.start_event_scope(root_id)
    child_id = event_system.create_event(
        **{**sample_event, "details": {"message": "Child message"}}
    )

    # Format chain
    formatted = event_system.format_event_chain(child_id)

    # Verify both events are included
    assert "Test message" in formatted
    assert "Child message" in formatted
    assert formatted.count("MESSAGE_SENT") == 2
