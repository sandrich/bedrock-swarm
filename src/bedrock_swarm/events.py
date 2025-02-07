"""Event system for tracking agent and tool interactions."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from .types import Event, EventType


class EventSystem:
    """System for tracking and managing events in the agent swarm.

    This class provides:
    1. Event creation and storage
    2. Event querying and filtering
    3. Event relationship tracking (parent/child)
    4. Chronological event ordering
    """

    def __init__(self) -> None:
        """Initialize the event system."""
        self.events: List[Event] = []
        self.current_event_id: Optional[str] = None

    def create_event(
        self,
        type: EventType,
        agent_name: str,
        run_id: str,
        thread_id: str,
        details: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Create and record a new event.

        Args:
            type: Type of event
            agent_name: Name of agent involved
            run_id: ID of the run this event belongs to
            thread_id: ID of the thread this event belongs to
            details: Event-specific details
            metadata: Optional additional metadata

        Returns:
            ID of the created event
        """
        event_id = str(uuid4())
        event: Event = {
            "id": event_id,
            "type": type,
            "timestamp": datetime.now().isoformat(),
            "agent_name": agent_name,
            "run_id": run_id,
            "thread_id": thread_id,
            "parent_event_id": self.current_event_id,
            "details": details,
            "metadata": metadata or {},
        }

        self.events.append(event)
        return event_id

    def start_event_scope(self, event_id: str) -> None:
        """Start a new event scope.

        This sets the current event as the parent for any new events
        until the scope is ended.

        Args:
            event_id: ID of the event to set as current
        """
        self.current_event_id = event_id

    def end_event_scope(self) -> None:
        """End the current event scope."""
        self.current_event_id = None

    def get_events(
        self,
        run_id: Optional[str] = None,
        thread_id: Optional[str] = None,
        agent_name: Optional[str] = None,
        event_type: Optional[EventType] = None,
    ) -> List[Event]:
        """Get events matching the specified filters.

        Args:
            run_id: Optional run ID to filter by
            thread_id: Optional thread ID to filter by
            agent_name: Optional agent name to filter by
            event_type: Optional event type to filter by

        Returns:
            List of matching events in chronological order
        """
        filtered = self.events

        if run_id:
            filtered = [e for e in filtered if e["run_id"] == run_id]
        if thread_id:
            filtered = [e for e in filtered if e["thread_id"] == thread_id]
        if agent_name:
            filtered = [e for e in filtered if e["agent_name"] == agent_name]
        if event_type:
            filtered = [e for e in filtered if e["type"] == event_type]

        return filtered

    def get_event_chain(self, event_id: str) -> List[Event]:
        """Get the chain of events leading to the specified event.

        This follows the parent_event_id links to build the chain.

        Args:
            event_id: ID of the event to get the chain for

        Returns:
            List of events in the chain, from root to specified event
        """
        chain = []
        current = next((e for e in self.events if e["id"] == event_id), None)

        while current:
            chain.append(current)
            if current["parent_event_id"]:
                current = next(
                    (e for e in self.events if e["id"] == current["parent_event_id"]),
                    None,
                )
            else:
                break

        return list(reversed(chain))  # Return in chronological order

    def format_event(self, event: Event) -> str:
        """Format an event for display.

        Args:
            event: Event to format

        Returns:
            Formatted string representation of the event
        """
        # Parse timestamp for formatting
        timestamp = datetime.fromisoformat(event["timestamp"])
        time_str = timestamp.strftime("%H:%M:%S.%f")[:-3]

        # Format basic event info
        lines = [
            f"[{time_str}] {event['type'].upper()} - Agent: {event['agent_name']}",
        ]

        # Add event details
        if event["details"]:
            for key, value in event["details"].items():
                if isinstance(value, dict):
                    lines.append(f"  {key}:")
                    for k, v in value.items():
                        lines.append(f"    {k}: {v}")
                else:
                    lines.append(f"  {key}: {value}")

        # Add metadata if present
        if event["metadata"]:
            lines.append("  Metadata:")
            for key, value in event["metadata"].items():
                lines.append(f"    {key}: {value}")

        return "\n".join(lines)

    def format_event_chain(self, event_id: str) -> str:
        """Format a chain of events for display.

        Args:
            event_id: ID of the event to get the chain for

        Returns:
            Formatted string representation of the event chain
        """
        chain = self.get_event_chain(event_id)
        return "\n\n".join(self.format_event(event) for event in chain)
