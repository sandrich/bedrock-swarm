import pytest
from datetime import datetime, timedelta

from bedrock_swarm.memory.base import Message, SimpleMemory

@pytest.fixture
def memory():
    return SimpleMemory()

@pytest.fixture
def sample_messages():
    now = datetime.now()
    return [
        Message(
            role="human",
            content="Hello",
            timestamp=now - timedelta(minutes=5)
        ),
        Message(
            role="assistant",
            content="Hi there!",
            timestamp=now - timedelta(minutes=4)
        ),
        Message(
            role="human",
            content="How are you?",
            timestamp=now - timedelta(minutes=3)
        ),
        Message(
            role="assistant",
            content="I'm doing well, thanks!",
            timestamp=now - timedelta(minutes=2)
        )
    ]

@pytest.mark.asyncio
async def test_add_message(memory):
    """Test adding a message to memory"""
    message = Message(
        role="human",
        content="test",
        timestamp=datetime.now()
    )
    
    await memory.add_message(message)
    messages = await memory.get_messages()
    
    assert len(messages) == 1
    assert messages[0].role == "human"
    assert messages[0].content == "test"

@pytest.mark.asyncio
async def test_get_messages_with_limit(memory, sample_messages):
    """Test getting messages with a limit"""
    for message in sample_messages:
        await memory.add_message(message)
    
    messages = await memory.get_messages(limit=2)
    assert len(messages) == 2
    assert messages[-1].content == "I'm doing well, thanks!"

@pytest.mark.asyncio
async def test_get_messages_by_role(memory, sample_messages):
    """Test getting messages filtered by role"""
    for message in sample_messages:
        await memory.add_message(message)
    
    human_messages = await memory.get_messages(role="human")
    assert len(human_messages) == 2
    assert all(m.role == "human" for m in human_messages)
    
    assistant_messages = await memory.get_messages(role="assistant")
    assert len(assistant_messages) == 2
    assert all(m.role == "assistant" for m in assistant_messages)

@pytest.mark.asyncio
async def test_get_messages_by_time(memory, sample_messages):
    """Test getting messages filtered by time"""
    for message in sample_messages:
        await memory.add_message(message)
    
    now = datetime.now()
    messages = await memory.get_messages(
        after=now - timedelta(minutes=3),
        before=now - timedelta(minutes=1)
    )
    
    assert len(messages) == 1
    assert messages[0].content == "I'm doing well, thanks!"

@pytest.mark.asyncio
async def test_clear_memory(memory, sample_messages):
    """Test clearing memory"""
    for message in sample_messages:
        await memory.add_message(message)
    
    await memory.clear()
    messages = await memory.get_messages()
    
    assert len(messages) == 0

@pytest.mark.asyncio
async def test_message_metadata(memory):
    """Test message metadata handling"""
    message = Message(
        role="system",
        content="test",
        timestamp=datetime.now(),
        metadata={"key": "value"}
    )
    
    await memory.add_message(message)
    messages = await memory.get_messages()
    
    assert len(messages) == 1
    assert messages[0].metadata == {"key": "value"} 