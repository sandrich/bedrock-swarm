"""Tests for the memory module."""

from datetime import datetime

from bedrock_swarm.memory.base import Message, SimpleMemory


def test_message_creation():
    """Test message creation."""
    message = Message(
        role="user",
        content="Test message",
        timestamp=datetime.now(),
    )
    assert message.role == "user"
    assert message.content == "Test message"
    assert isinstance(message.timestamp, datetime)


def test_simple_memory_initialization():
    """Test simple memory initialization."""
    memory = SimpleMemory()
    assert memory.messages == []


def test_add_message():
    """Test adding a message."""
    memory = SimpleMemory()
    message = Message(
        role="user",
        content="Test message",
        timestamp=datetime.now(),
    )
    memory.add_message(message)
    assert len(memory.messages) == 1
    assert memory.messages[0] == message


def test_get_messages():
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


def test_clear_messages():
    """Test clearing messages."""
    memory = SimpleMemory()
    message = Message(
        role="user",
        content="Test message",
        timestamp=datetime.now(),
    )
    memory.add_message(message)
    memory.clear_messages()
    assert len(memory.messages) == 0


def test_get_last_message():
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


def test_get_last_message_empty():
    """Test getting last message from empty memory."""
    memory = SimpleMemory()
    assert memory.get_last_message() is None


def test_get_messages_by_role():
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
