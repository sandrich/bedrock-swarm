import json
import pytest
from unittest.mock import AsyncMock, Mock, patch

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
        mock = Mock()
        mock_client.return_value = mock
        yield mock

@pytest.fixture
def agent(aws_config, mock_bedrock_client):
    return BedrockAgent(
        name="test_agent",
        model_id="anthropic.claude-v2",
        aws_config=aws_config,
        instructions="You are a helpful AI assistant."
    )

def test_agent_initialization(agent):
    """Test that agent is initialized with correct attributes"""
    assert agent.name == "test_agent"
    assert agent.model_id == "anthropic.claude-v2"
    assert agent.instructions == "You are a helpful AI assistant."
    assert isinstance(agent.tools, list)
    assert len(agent.tools) == 0

@pytest.mark.asyncio
async def test_agent_invoke_claude(agent, mock_bedrock_client):
    """Test that agent can invoke Claude model"""
    mock_response = {
        "completion": "Test response",
        "stop_reason": "stop",
    }
    mock_bedrock_client.invoke_model.return_value = {
        "body": Mock(read=Mock(return_value=json.dumps(mock_response).encode()))
    }
    
    response = await agent.invoke("Test message")
    
    assert response == "Test response"
    mock_bedrock_client.invoke_model.assert_called_once()
    call_args = mock_bedrock_client.invoke_model.call_args[1]
    assert call_args["modelId"] == "anthropic.claude-v2"
    assert "Human: Test message\n\nAssistant:" in json.loads(call_args["body"])["prompt"]

@pytest.mark.asyncio
async def test_agent_invoke_with_system_prompt(agent, mock_bedrock_client):
    """Test that agent includes system prompt in invocation"""
    mock_response = {
        "completion": "Test response",
        "stop_reason": "stop",
    }
    mock_bedrock_client.invoke_model.return_value = {
        "body": Mock(read=Mock(return_value=json.dumps(mock_response).encode()))
    }
    
    await agent.invoke("Test message")
    
    call_args = mock_bedrock_client.invoke_model.call_args[1]
    prompt = json.loads(call_args["body"])["prompt"]
    assert agent.instructions in prompt
    assert "Test message" in prompt

@pytest.mark.asyncio
async def test_agent_process_message_with_tools(agent, mock_bedrock_client):
    """Test that agent can process messages with tools"""
    # Create a mock tool
    mock_tool = Mock()
    mock_tool.name = "test_tool"
    mock_tool.description = "A test tool"
    mock_tool.get_schema.return_value = {
        "name": "test_tool",
        "description": "A test tool",
        "parameters": {
            "type": "object",
            "properties": {
                "param": {"type": "string"}
            }
        }
    }
    mock_tool.execute = AsyncMock(return_value="Tool result")
    
    # Add tool to agent
    agent.add_tool(mock_tool)
    
    # Mock model response with tool call
    mock_response = {
        "completion": "Let me use the tool",
        "stop_reason": "tool_call",
        "tool_calls": [{
            "name": "test_tool",
            "parameters": {"param": "test"}
        }]
    }
    mock_bedrock_client.invoke_model.return_value = {
        "body": Mock(read=Mock(return_value=json.dumps(mock_response).encode()))
    }
    
    response = await agent.process_message("Use the test tool")
    
    assert "Tool result" in response
    mock_tool.execute.assert_called_once_with(param="test") 