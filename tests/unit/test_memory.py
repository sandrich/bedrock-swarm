"""Tests for the memory module."""

from datetime import datetime, timedelta

from bedrock_swarm.memory.base import Message, SimpleMemory


def test_message_creation() -> None:
    """Test message creation."""
    timestamp = datetime.now()
    metadata = {"key": "value"}
    message = Message(
        role="human", content="Test message", timestamp=timestamp, metadata=metadata
    )
    assert message.role == "human"
    assert message.content == "Test message"
    assert message.timestamp == timestamp
    assert message.metadata == metadata


def test_simple_memory_initialization() -> None:
    """Test simple memory initialization."""
    memory = SimpleMemory()
    assert memory.get_messages() == []

    # Test custom max size
    memory = SimpleMemory(max_size=10)
    assert memory.get_messages() == []


def test_add_message() -> None:
    """Test adding a message."""
    memory = SimpleMemory()
    message = Message(
        role="human",
        content="Test message",
        timestamp=datetime.now(),
    )
    memory.add_message(message)
    messages = memory.get_messages()
    assert len(messages) == 1
    assert messages[0] == message


def test_max_size_limit() -> None:
    """Test max size limit enforcement."""
    memory = SimpleMemory(max_size=2)

    # Add 3 messages
    messages = [
        Message(role="human", content=f"Message {i}", timestamp=datetime.now())
        for i in range(3)
    ]
    for msg in messages:
        memory.add_message(msg)

    # Should only keep last 2 messages
    stored_messages = memory.get_messages()
    assert len(stored_messages) == 2
    assert stored_messages == messages[-2:]


def test_get_messages_filtering() -> None:
    """Test message filtering options."""
    memory = SimpleMemory()

    # Create messages with different timestamps and roles
    now = datetime.now()
    messages = [
        Message(role="human", content="Message 1", timestamp=now - timedelta(hours=2)),
        Message(
            role="assistant", content="Message 2", timestamp=now - timedelta(hours=1)
        ),
        Message(role="human", content="Message 3", timestamp=now),
    ]

    for msg in messages:
        memory.add_message(msg)

    # Test limit
    limited_messages = memory.get_messages(limit=2)
    assert len(limited_messages) == 2
    assert limited_messages == messages[-2:]

    # Test before/after
    assert len(memory.get_messages(before=now - timedelta(minutes=30))) == 2
    assert len(memory.get_messages(after=now - timedelta(minutes=30))) == 1

    # Test role filter
    human_messages = memory.get_messages(role="human")
    assert len(human_messages) == 2
    assert all(msg.role == "human" for msg in human_messages)

    assistant_messages = memory.get_messages(role="assistant")
    assert len(assistant_messages) == 1
    assert all(msg.role == "assistant" for msg in assistant_messages)


def test_clear() -> None:
    """Test clearing messages."""
    memory = SimpleMemory()
    message = Message(
        role="human",
        content="Test message",
        timestamp=datetime.now(),
    )
    memory.add_message(message)
    assert len(memory.get_messages()) == 1

    memory.clear()
    assert len(memory.get_messages()) == 0


def test_get_messages() -> None:
    """Test getting messages."""
    memory = SimpleMemory()
    message1 = Message(
        role="user",
        content="Message 1",
        timestamp=datetime.now(),
    )
    message2 = Message(
        role="assistant",
        content="Message 2",
        timestamp=datetime.now(),
    )
    memory.add_message(message1)
    memory.add_message(message2)
    messages = memory.get_messages()
    assert len(messages) == 2
    assert messages[0] == message1
    assert messages[1] == message2


def test_get_last_message() -> None:
    """Test getting last message."""
    memory = SimpleMemory()
    message1 = Message(
        role="user",
        content="Message 1",
        timestamp=datetime.now(),
    )
    message2 = Message(
        role="assistant",
        content="Message 2",
        timestamp=datetime.now(),
    )
    memory.add_message(message1)
    memory.add_message(message2)
    last_message = memory.get_last_message()
    assert last_message == message2


def test_get_last_message_empty() -> None:
    """Test getting last message from empty memory."""
    memory = SimpleMemory()
    assert memory.get_last_message() is None


def test_get_messages_by_role() -> None:
    """Test getting messages by role."""
    memory = SimpleMemory()
    user_message = Message(
        role="user",
        content="User message",
        timestamp=datetime.now(),
    )
    assistant_message = Message(
        role="assistant",
        content="Assistant message",
        timestamp=datetime.now(),
    )
    memory.add_message(user_message)
    memory.add_message(assistant_message)
    user_messages = memory.get_messages_by_role("user")
    assistant_messages = memory.get_messages_by_role("assistant")
    assert len(user_messages) == 1
    assert len(assistant_messages) == 1
    assert user_messages[0] == user_message
    assert assistant_messages[0] == assistant_message
