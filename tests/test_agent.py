import pytest
from unittest.mock import Mock, patch

from bedrock_swarm.agents.base import BedrockAgent
from bedrock_swarm.config import AWSConfig

@pytest.fixture
def aws_config():
    return AWSConfig(
        region="us-west-2",
        profile="default"
    )

@pytest.fixture
def mock_bedrock_client():
    with patch("boto3.client") as mock_client:
        yield mock_client.return_value

@pytest.fixture
def agent(aws_config, mock_bedrock_client):
    return BedrockAgent(
        name="test_agent",
        model_id="anthropic.claude-v2",
        aws_config=aws_config
    )

def test_agent_initialization(agent):
    """Test that agent is initialized with correct attributes"""
    assert agent.name == "test_agent"
    assert agent.model_id == "anthropic.claude-v2"
    assert isinstance(agent.tools, list)
    assert len(agent.tools) == 0

@pytest.mark.asyncio
async def test_agent_invoke(agent, mock_bedrock_client):
    """Test that agent can invoke the model"""
    mock_response = {
        "completion": "Test response",
        "stop_reason": "stop",
    }
    mock_bedrock_client.invoke_model.return_value = mock_response
    
    response = await agent.invoke("Test message")
    
    assert response == "Test response"
    mock_bedrock_client.invoke_model.assert_called_once()

def test_agent_add_tool(agent):
    """Test that agent can add tools"""
    mock_tool = Mock()
    mock_tool.name = "test_tool"
    
    agent.add_tool(mock_tool)
    
    assert len(agent.tools) == 1
    assert agent.tools[0] == mock_tool

@pytest.mark.asyncio
async def test_agent_process_message(agent):
    """Test that agent can process messages"""
    with patch.object(agent, "invoke") as mock_invoke:
        mock_invoke.return_value = "Test response"
        
        response = await agent.process_message("Test message")
        
        assert response == "Test response"
        mock_invoke.assert_called_once_with("Test message")

def test_simple():
    assert True 