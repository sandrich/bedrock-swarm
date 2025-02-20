"""Tests for event system implementation."""

from datetime import datetime
from typing import Dict

import pytest

from bedrock_swarm.events import EventSystem
from bedrock_swarm.types import Event, EventType


@pytest.fixture
def event_system() -> EventSystem:
    """Create an event system instance."""
    return EventSystem()


def create_test_event(
    event_type: EventType = "agent_start",
    agent_name: str = "test_agent",
    run_id: str = "test_run",
    thread_id: str = "test_thread",
    details: Dict = None,
    parent_id: str = None,
) -> Event:
    """Create a test event with default values."""
    return {
        "id": "test_event",
        "type": event_type,
        "timestamp": datetime.now().isoformat(),
        "agent_name": agent_name,
        "run_id": run_id,
        "thread_id": thread_id,
        "parent_event_id": parent_id,
        "details": details or {},
        "metadata": {},
    }


def test_event_creation(event_system: EventSystem) -> None:
    """Test event creation and storage."""
    # Create basic event
    event_id = event_system.create_event(
        type="agent_start",
        agent_name="test_agent",
        run_id="test_run",
        thread_id="test_thread",
        details={"message": "Test message"},
    )

    # Verify event was stored
    assert len(event_system.events) == 1
    event = event_system.events[0]
    assert event["id"] == event_id
    assert event["type"] == "agent_start"
    assert event["agent_name"] == "test_agent"
    assert event["run_id"] == "test_run"
    assert event["thread_id"] == "test_thread"
    assert event["details"] == {"message": "Test message"}
    assert event["parent_event_id"] is None
    assert isinstance(event["timestamp"], str)
    assert isinstance(event["metadata"], dict)

    # Create event with metadata
    event_id = event_system.create_event(
        type="tool_start",
        agent_name="test_agent",
        run_id="test_run",
        thread_id="test_thread",
        details={"tool": "test_tool"},
        metadata={"priority": "high"},
    )

    # Verify metadata was stored
    event = event_system.events[1]
    assert event["metadata"] == {"priority": "high"}


def test_event_scoping(event_system: EventSystem) -> None:
    """Test event scope management."""
    # Create parent event
    parent_id = event_system.create_event(
        type="agent_start",
        agent_name="test_agent",
        run_id="test_run",
        thread_id="test_thread",
        details={"message": "Parent event"},
    )

    # Start scope with parent
    event_system.start_event_scope(parent_id)

    # Create child event
    child_id = event_system.create_event(
        type="tool_start",
        agent_name="test_agent",
        run_id="test_run",
        thread_id="test_thread",
        details={"message": "Child event"},
    )

    # Verify parent-child relationship
    child_event = next(e for e in event_system.events if e["id"] == child_id)
    assert child_event["parent_event_id"] == parent_id

    # End scope
    event_system.end_event_scope()

    # Create another event
    new_id = event_system.create_event(
        type="agent_complete",
        agent_name="test_agent",
        run_id="test_run",
        thread_id="test_thread",
        details={"message": "New event"},
    )

    # Verify no parent relationship
    new_event = next(e for e in event_system.events if e["id"] == new_id)
    assert new_event["parent_event_id"] is None


def test_event_filtering(event_system: EventSystem) -> None:
    """Test event filtering functionality."""
    # Create events with different attributes
    event_system.create_event(
        type="agent_start",
        agent_name="agent1",
        run_id="run1",
        thread_id="thread1",
        details={},
    )
    event_system.create_event(
        type="tool_start",
        agent_name="agent1",
        run_id="run1",
        thread_id="thread1",
        details={},
    )
    event_system.create_event(
        type="agent_start",
        agent_name="agent2",
        run_id="run2",
        thread_id="thread2",
        details={},
    )

    # Filter by run ID
    run1_events = event_system.get_events(run_id="run1")
    assert len(run1_events) == 2
    assert all(e["run_id"] == "run1" for e in run1_events)

    # Filter by thread ID
    thread2_events = event_system.get_events(thread_id="thread2")
    assert len(thread2_events) == 1
    assert all(e["thread_id"] == "thread2" for e in thread2_events)

    # Filter by agent name
    agent1_events = event_system.get_events(agent_name="agent1")
    assert len(agent1_events) == 2
    assert all(e["agent_name"] == "agent1" for e in agent1_events)

    # Filter by event type
    tool_events = event_system.get_events(event_type="tool_start")
    assert len(tool_events) == 1
    assert all(e["type"] == "tool_start" for e in tool_events)

    # Combined filters
    combined = event_system.get_events(
        run_id="run1",
        thread_id="thread1",
        agent_name="agent1",
        event_type="agent_start",
    )
    assert len(combined) == 1
    assert combined[0]["run_id"] == "run1"
    assert combined[0]["thread_id"] == "thread1"
    assert combined[0]["agent_name"] == "agent1"
    assert combined[0]["type"] == "agent_start"


def test_event_chain(event_system: EventSystem) -> None:
    """Test event chain retrieval."""
    # Create chain of events
    root_id = event_system.create_event(
        type="agent_start",
        agent_name="test_agent",
        run_id="test_run",
        thread_id="test_thread",
        details={"message": "Root event"},
    )

    event_system.start_event_scope(root_id)
    child1_id = event_system.create_event(
        type="tool_start",
        agent_name="test_agent",
        run_id="test_run",
        thread_id="test_thread",
        details={"message": "Child event 1"},
    )

    event_system.start_event_scope(child1_id)
    child2_id = event_system.create_event(
        type="tool_complete",
        agent_name="test_agent",
        run_id="test_run",
        thread_id="test_thread",
        details={"message": "Child event 2"},
    )

    # Get chain for leaf event
    chain = event_system.get_event_chain(child2_id)

    # Verify chain order and relationships
    assert len(chain) == 3
    assert chain[0]["id"] == root_id
    assert chain[1]["id"] == child1_id
    assert chain[2]["id"] == child2_id
    assert chain[1]["parent_event_id"] == root_id
    assert chain[2]["parent_event_id"] == child1_id


def test_event_formatting(event_system: EventSystem) -> None:
    """Test event formatting."""
    # Create event with various details
    event_id = event_system.create_event(
        type="tool_start",
        agent_name="test_agent",
        run_id="test_run",
        thread_id="test_thread",
        details={
            "tool_name": "calculator",
            "arguments": {
                "expression": "2 + 2",
                "format": "decimal",
            },
        },
        metadata={
            "priority": "high",
            "source": "user",
        },
    )

    # Format single event
    formatted = event_system.format_event(event_system.events[0])
    assert "[" in formatted  # Has timestamp
    assert "TOOL_START" in formatted  # Has event type
    assert "test_agent" in formatted  # Has agent name
    assert "calculator" in formatted  # Has tool name
    assert "2 + 2" in formatted  # Has nested argument
    assert "priority: high" in formatted  # Has metadata

    # Format event chain
    chain_str = event_system.format_event_chain(event_id)
    assert formatted in chain_str  # Chain includes the event
