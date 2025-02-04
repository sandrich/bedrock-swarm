import json
import pytest
from unittest.mock import AsyncMock, Mock, patch
from botocore.exceptions import BotoCoreError, ClientError

from bedrock_swarm.agents.base import BedrockAgent
from bedrock_swarm.config import AWSConfig
from bedrock_swarm.exceptions import ModelInvokeError, ResponseParsingError, ToolExecutionError, ToolNotFoundError, ToolError
from bedrock_swarm.tools.base import BaseTool
from bedrock_swarm.tools.web import WebSearchTool
from bedrock_swarm.tools.factory import ToolFactory

class MockTool(BaseTool):
    """Mock tool for testing."""
    
    def __init__(self):
        self.execute = AsyncMock(return_value="Tool result")
    
    @property
    def name(self) -> str:
        return "test_tool"
    
    @property
    def description(self) -> str:
        return "Test tool"
    
    def get_schema(self):
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "param": {
                        "type": "string"
                    }
                }
            }
        }
    
    async def execute(self, **kwargs):
        return await self.execute(**kwargs)

@pytest.fixture(autouse=True)
def clear_tool_registry():
    """Clear tool registry before each test."""
    ToolFactory.clear()
    yield
    ToolFactory.clear()

@pytest.fixture
def agent():
    """Create a test agent."""
    config = AWSConfig(region="us-west-2", profile="default")
    with patch("boto3.Session") as mock_session:
        session = Mock()
        session.client.return_value = Mock()
        mock_session.return_value = session
        
        return BedrockAgent(
            name="test_agent",
            model_id="anthropic.claude-v2",
            aws_config=config
        )

@pytest.fixture
def mock_bedrock_client(agent):
    """Get the mocked Bedrock client from the agent."""
    return agent.bedrock

@pytest.mark.asyncio
async def test_agent_process_message_claude(agent, mock_bedrock_client):
    """Test that agent can process message with Claude model"""
    mock_response = {
        "completion": "Test response",
        "stop_reason": "stop",
    }
    mock_bedrock_client.invoke_model.return_value = {
        "body": Mock(read=Mock(return_value=json.dumps(mock_response).encode()))
    }

    response = await agent.process_message("Test message")
    assert response == "Test response"

@pytest.mark.asyncio
async def test_agent_process_message_titan():
    """Test that agent can process message with Titan model"""
    config = AWSConfig(region="us-west-2", profile="default")
    mock_client = Mock()
    mock_response = {
        "results": [{"outputText": "Test response"}]
    }
    mock_client.invoke_model.return_value = {
        "body": Mock(read=Mock(return_value=json.dumps(mock_response).encode()))
    }

    with patch("boto3.Session") as mock_session:
        session = Mock()
        session.client.return_value = mock_client
        mock_session.return_value = session

        agent = BedrockAgent(
            name="titan_agent",
            model_id="amazon.titan-text-express-v1",
            aws_config=config
        )

        response = await agent.process_message("Test message")
        assert response == "Test response"

@pytest.mark.asyncio
async def test_agent_process_message_jurassic():
    """Test that agent can process message with Jurassic model"""
    config = AWSConfig(region="us-west-2", profile="default")
    mock_client = Mock()
    mock_response = {
        "completions": [{
            "data": {"text": "Test response"}
        }]
    }
    mock_client.invoke_model.return_value = {
        "body": Mock(read=Mock(return_value=json.dumps(mock_response).encode()))
    }

    with patch("boto3.Session") as mock_session:
        session = Mock()
        session.client.return_value = mock_client
        mock_session.return_value = session

        agent = BedrockAgent(
            name="jurassic_agent",
            model_id="ai21.j2-ultra-v1",
            aws_config=config
        )

        response = await agent.process_message("Test message")
        assert response == "Test response"

@pytest.mark.asyncio
async def test_agent_process_message_cohere():
    """Test that agent can process message with Cohere model"""
    config = AWSConfig(region="us-west-2", profile="default")
    mock_client = Mock()
    mock_response = {
        "generations": [{
            "text": "Test response"
        }]
    }
    mock_client.invoke_model.return_value = {
        "body": Mock(read=Mock(return_value=json.dumps(mock_response).encode()))
    }

    with patch("boto3.Session") as mock_session:
        session = Mock()
        session.client.return_value = mock_client
        mock_session.return_value = session

        agent = BedrockAgent(
            name="cohere_agent",
            model_id="cohere.command-text-v14",
            aws_config=config
        )

        response = await agent.process_message("Test message")
        assert response == "Test response"

@pytest.mark.asyncio
async def test_agent_response_fallback():
    """Test that agent can handle unexpected response formats"""
    config = AWSConfig(region="us-west-2", profile="default")
    mock_client = Mock()
    mock_response = {
        "unexpected_key": {
            "text": "Test response"
        }
    }
    mock_client.invoke_model.return_value = {
        "body": Mock(read=Mock(return_value=json.dumps(mock_response).encode()))
    }

    with patch("boto3.Session") as mock_session:
        session = Mock()
        session.client.return_value = mock_client
        mock_session.return_value = session

        agent = BedrockAgent(
            name="fallback_agent",
            model_id="anthropic.claude-v2",
            aws_config=config
        )

        with pytest.raises(ResponseParsingError) as exc_info:
            await agent.process_message("Test message")

@pytest.mark.asyncio
async def test_agent_process_message_with_system_prompt(agent, mock_bedrock_client):
    """Test that agent includes system prompt in process_message"""
    mock_response = {
        "completion": "Test response",
        "stop_reason": "stop",
    }
    mock_bedrock_client.invoke_model.return_value = {
        "body": Mock(read=Mock(return_value=json.dumps(mock_response).encode()))
    }

    await agent.process_message("Test message")
    
    call_args = mock_bedrock_client.invoke_model.call_args[1]
    request_body = json.loads(call_args["body"])
    assert "Human: Test message" in request_body["prompt"]

@pytest.mark.asyncio
async def test_agent_process_message_with_tools(agent, mock_bedrock_client):
    """Test that agent can process messages with tools (Claude only)"""
    # Add tool to agent
    tool = MockTool()
    agent.add_tool(tool)

    # Set up mock response
    mock_response = {
        "completion": "Test response with tool call",
        "stop_reason": "stop_sequence",
        "tool_calls": [{
            "type": "function",
            "function": {
                "name": "test_tool",
                "arguments": "{\"param\": \"test\"}"
            }
        }]
    }
    mock_bedrock_client.invoke_model.return_value = {
        "body": Mock(read=Mock(return_value=json.dumps(mock_response).encode()))
    }

    # Process message
    response = await agent.process_message("Test message")
    assert response == "Test response with tool call"

    # Verify tool was called
    tool.execute.assert_called_once_with(param="test")

@pytest.mark.asyncio
async def test_agent_process_message_with_tools_non_claude():
    """Test that tools are ignored for non-Claude models"""
    config = AWSConfig(region="us-west-2", profile="default")
    mock_client = Mock()
    mock_response = {
        "results": [{"outputText": "Test response"}]
    }
    mock_client.invoke_model.return_value = {
        "body": Mock(read=Mock(return_value=json.dumps(mock_response).encode()))
    }

    with patch("boto3.Session") as mock_session:
        session = Mock()
        session.client.return_value = mock_client
        mock_session.return_value = session

        agent = BedrockAgent(
            name="titan_agent",
            model_id="amazon.titan-text-express-v1",
            aws_config=config
        )

        # Add tool to agent
        tool = MockTool()
        agent.add_tool(tool)

        # Process message
        response = await agent.process_message("Test message")

        # Verify request body doesn't include tools
        call_args = mock_client.invoke_model.call_args[1]
        request_body = json.loads(call_args["body"])
        assert "tools" not in request_body

        # Verify tool was not called
        tool.execute.assert_not_called()

@pytest.mark.asyncio
async def test_agent_api_error(agent, mock_bedrock_client):
    """Test that agent process_message fails with API error"""
    mock_bedrock_client.invoke_model.side_effect = ClientError(
        error_response={"Error": {"Code": "ThrottlingException"}},
        operation_name="InvokeModel"
    )

    with pytest.raises(ModelInvokeError) as exc_info:
        await agent.process_message("Test message")

@pytest.mark.asyncio
async def test_agent_invalid_response(agent, mock_bedrock_client):
    """Test that agent process_message fails with invalid response"""
    mock_response = {
        "invalid": "response"
    }
    mock_bedrock_client.invoke_model.return_value = {
        "body": Mock(read=Mock(return_value=json.dumps(mock_response).encode()))
    }

    with pytest.raises(ResponseParsingError) as exc_info:
        await agent.process_message("Test message")

@pytest.mark.asyncio
async def test_agent_invalid_json(agent, mock_bedrock_client):
    """Test that agent process_message fails with invalid JSON"""
    mock_bedrock_client.invoke_model.return_value = {
        "body": Mock(read=Mock(return_value=b"invalid json"))
    }

    with pytest.raises(ResponseParsingError) as exc_info:
        await agent.process_message("Test message")

@pytest.mark.asyncio
async def test_agent_tool_not_found(agent, mock_bedrock_client):
    """Test that agent fails when tool is not found"""
    mock_response = {
        "completion": "Let me use the tool",
        "tool_calls": [{
            "type": "function",
            "function": {
                "name": "nonexistent_tool",
                "arguments": "{}"
            }
        }]
    }
    mock_bedrock_client.invoke_model.return_value = {
        "body": Mock(read=Mock(return_value=json.dumps(mock_response).encode()))
    }

    with pytest.raises(ToolNotFoundError):
        await agent.process_message("Use the tool")

@pytest.mark.asyncio
async def test_agent_tool_execution_error(agent, mock_bedrock_client):
    """Test that agent fails when tool execution fails"""
    # Create a mock tool that raises an error
    tool = MockTool()
    tool.execute = AsyncMock(side_effect=Exception("Tool execution failed"))
    agent.add_tool(tool)

    # Set up mock response with tool call
    mock_response = {
        "completion": "Test response with tool call",
        "stop_reason": "stop_sequence",
        "tool_calls": [{
            "type": "function",
            "function": {
                "name": "test_tool",
                "arguments": "{\"param\": \"test\"}"
            }
        }]
    }
    mock_bedrock_client.invoke_model.return_value = {
        "body": Mock(read=Mock(return_value=json.dumps(mock_response).encode()))
    }

    # Process message should raise ToolExecutionError
    with pytest.raises(ToolExecutionError):
        await agent.process_message("Test message")

def test_add_tool_by_name(agent):
    """Test adding a tool by name."""
    tool = agent.add_tool("WebSearchTool")
    assert isinstance(tool, WebSearchTool)
    assert tool.name in agent._tools
    assert agent._tools[tool.name] == tool

def test_add_invalid_tool_type(agent):
    """Test adding an invalid tool type."""
    with pytest.raises(ToolError):
        agent.add_tool("InvalidTool") 