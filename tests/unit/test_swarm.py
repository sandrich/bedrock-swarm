import pytest
from unittest.mock import AsyncMock, Mock, patch
from uuid import UUID

from bedrock_swarm.agents.base import BedrockAgent
from bedrock_swarm.config import AWSConfig
from bedrock_swarm.swarm.base import Swarm

@pytest.fixture
def aws_config():
    return AWSConfig(
        region="us-west-2",
        profile="default"
    )

@pytest.fixture
def mock_bedrock_client():
    with patch("boto3.client") as mock_client:
        mock = Mock()
        mock_client.return_value = mock
        yield mock

@pytest.fixture
def mock_agent(aws_config, mock_bedrock_client):
    agent = BedrockAgent(
        name="test_agent",
        model_id="anthropic.claude-v2",
        aws_config=aws_config,
        instructions="You are a helpful AI assistant."
    )
    agent.process_message = AsyncMock(return_value="Test response")
    return agent

@pytest.fixture
def swarm():
    return Swarm(max_rounds=3)

def test_swarm_initialization(swarm):
    """Test that swarm is initialized correctly"""
    assert swarm.max_rounds == 3
    assert len(swarm.agents) == 0
    assert swarm._round == 0

def test_add_agent(swarm, mock_agent):
    """Test adding an agent to the swarm"""
    agent_id = swarm.add_agent(mock_agent)
    
    assert isinstance(agent_id, UUID)
    assert len(swarm.agents) == 1
    assert swarm.agents[agent_id] == mock_agent

def test_get_agent(swarm, mock_agent):
    """Test getting an agent by ID"""
    agent_id = swarm.add_agent(mock_agent)
    retrieved_agent = swarm.get_agent(agent_id)
    
    assert retrieved_agent == mock_agent
    assert swarm.get_agent(UUID('00000000-0000-0000-0000-000000000000')) is None

def test_remove_agent(swarm, mock_agent):
    """Test removing an agent from the swarm"""
    agent_id = swarm.add_agent(mock_agent)
    
    assert swarm.remove_agent(agent_id) is True
    assert len(swarm.agents) == 0
    assert swarm.remove_agent(agent_id) is False

@pytest.mark.asyncio
async def test_broadcast(swarm, mock_agent):
    """Test broadcasting a message to all agents"""
    agent_id1 = swarm.add_agent(mock_agent)
    agent_id2 = swarm.add_agent(mock_agent)
    
    responses = await swarm.broadcast("Test message")
    
    assert len(responses) == 2
    assert all(r == "Test response" for r in responses)
    
    # Test excluding agents
    responses = await swarm.broadcast("Test message", exclude=[agent_id1])
    assert len(responses) == 1

@pytest.mark.asyncio
async def test_discuss(swarm, mock_agent):
    """Test agent discussion"""
    swarm.add_agent(mock_agent)
    swarm.add_agent(mock_agent)
    
    history = await swarm.discuss("Test topic", rounds=2)
    
    assert len(history) == 2  # Initial round + 1 discussion round
    assert history[0]["round"] == 0
    assert history[0]["topic"] == "Test topic"
    assert len(history[0]["responses"]) == 2
    
    assert history[1]["round"] == 1
    assert len(history[1]["responses"]) == 2
    
    # Test memory storage
    messages = await swarm.memory.get_messages()
    assert len(messages) > 0
    assert any(m.metadata.get("round") == 1 for m in messages) 