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

    # Test getting all messages
    all_messages = memory.get_messages()
    assert len(all_messages) == 3
    assert all_messages == messages  # Should be in chronological order


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

    # Test getting all messages
    all_messages = memory.get_messages()
    assert len(all_messages) == 2
    assert any(m.role == "user" for m in all_messages)
    assert any(m.role == "assistant" for m in all_messages)


def test_get_messages_by_type() -> None:
    """Test getting messages by type."""
    memory = SimpleMemory()

    # Add messages with different types
    messages = [
        Message(
            role="user",
            content="User message",
            timestamp=datetime.now(),
            metadata={"type": "user_message"},
        ),
        Message(
            role="system",
            content="Tool result",
            timestamp=datetime.now(),
            metadata={"type": "tool_result", "tool_call_id": "123"},
        ),
        Message(
            role="assistant",
            content="Assistant message",
            timestamp=datetime.now(),
            metadata={"type": "assistant_response"},
        ),
    ]

    for msg in messages:
        memory.add_message(msg)

    # Test filtering by type
    user_messages = memory.get_messages_by_type("user_message")
    assert len(user_messages) == 1
    assert user_messages[0].content == "User message"

    tool_results = memory.get_messages_by_type("tool_result")
    assert len(tool_results) == 1
    assert tool_results[0].content == "Tool result"
    assert tool_results[0].metadata["tool_call_id"] == "123"


def test_get_tool_results() -> None:
    """Test getting tool execution results."""
    memory = SimpleMemory()

    # Add tool result messages
    tool_results = [
        Message(
            role="system",
            content=f"Tool result {i}",
            timestamp=datetime.now(),
            metadata={"type": "tool_result", "tool_call_id": str(i)},
        )
        for i in range(3)
    ]

    # Add other message types
    other_messages = [
        Message(
            role="user",
            content="User message",
            timestamp=datetime.now(),
            metadata={"type": "user_message"},
        ),
        Message(
            role="assistant",
            content="Assistant message",
            timestamp=datetime.now(),
            metadata={"type": "assistant_response"},
        ),
    ]

    for msg in tool_results + other_messages:
        memory.add_message(msg)

    # Test getting all tool results
    all_results = memory.get_tool_results()
    assert len(all_results) == 3
    assert all(msg.metadata["type"] == "tool_result" for msg in all_results)

    # Test with limit
    limited_results = memory.get_tool_results(limit=2)
    assert len(limited_results) == 2
    assert limited_results[-1].content == "Tool result 2"


def test_get_conversation_summary() -> None:
    """Test getting conversation summary."""
    memory = SimpleMemory()

    # Add conversation messages
    messages = [
        Message(
            role="user",
            content="Question 1",
            timestamp=datetime.now(),
            metadata={"type": "user_message"},
        ),
        Message(
            role="assistant",
            content="Answer 1",
            timestamp=datetime.now(),
            metadata={"type": "assistant_response"},
        ),
        Message(
            role="user",
            content="Question 2",
            timestamp=datetime.now(),
            metadata={"type": "user_message"},
        ),
        Message(
            role="assistant",
            content="Tool call",
            timestamp=datetime.now(),
            metadata={"type": "tool_call_intent"},
        ),
        Message(
            role="user",
            content="Question 3",
            timestamp=datetime.now(),
            metadata={"type": "user_message"},
        ),
    ]

    for msg in messages:
        memory.add_message(msg)

    # Test getting summary
    summary = memory.get_conversation_summary(limit=2)
    assert len(summary) == 2

    # Check most recent exchanges
    assert summary[-1]["user"] == "Question 3"
    assert summary[-1]["assistant"] is None

    assert summary[-2]["user"] == "Question 2"
    assert summary[-2]["assistant"] == "Tool call"
    assert summary[-2]["has_tool_calls"] is True


def test_thread_management() -> None:
    """Test thread-specific memory management."""
    memory = SimpleMemory()

    # Add messages to different threads
    thread1_msg = Message(
        role="user",
        content="Thread 1 message",
        timestamp=datetime.now(),
        thread_id="thread1",
        metadata={"type": "user_message"},
    )
    thread2_msg = Message(
        role="user",
        content="Thread 2 message",
        timestamp=datetime.now(),
        thread_id="thread2",
        metadata={"type": "user_message"},
    )

    memory.add_message(thread1_msg)
    memory.add_message(thread2_msg)

    # Test thread-specific retrieval
    thread1_messages = memory.get_messages(thread_id="thread1")
    assert len(thread1_messages) == 1
    assert thread1_messages[0].content == "Thread 1 message"

    # Test thread clearing
    memory.clear_thread("thread1")
    assert len(memory.get_messages(thread_id="thread1")) == 0
    assert len(memory.get_messages(thread_id="thread2")) == 1

    # Test getting thread IDs
    assert set(memory.get_thread_ids()) == {"thread2"}


def test_memory_metadata() -> None:
    """Test handling of message metadata."""
    memory = SimpleMemory()

    # Add message with rich metadata
    message = Message(
        role="assistant",
        content="Response with tool call",
        timestamp=datetime.now(),
        thread_id="test_thread",
        metadata={
            "type": "tool_call_intent",
            "tool_calls": [{"id": "123", "name": "test_tool"}],
            "agent": "test_agent",
        },
    )

    memory.add_message(message)

    # Retrieve and verify metadata
    retrieved = memory.get_messages()[0]
    assert retrieved.metadata["type"] == "tool_call_intent"
    assert retrieved.metadata["tool_calls"][0]["id"] == "123"
    assert retrieved.metadata["agent"] == "test_agent"
