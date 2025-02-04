import json
from typing import Any, Dict, List, Optional, Union

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from ..config import AWSConfig
from ..tools.base import BaseTool
from ..tools.factory import ToolFactory
from ..exceptions import (
    AWSConfigError,
    InvalidModelError,
    ModelInvokeError,
    ResponseParsingError,
    ToolError,
    ToolExecutionError,
    ToolNotFoundError,
)

# List of supported model families
SUPPORTED_MODELS = {
    "anthropic.claude": {"versions": ["v1", "v2", "v2:1", "instant-v1"]},
    "amazon.titan": {"versions": ["text-express-v1", "text-lite-v1"]},
    "ai21.j2": {"versions": ["mid-v1", "ultra-v1"]},
    "cohere.command": {"versions": ["text-v14"]}
}

class BedrockAgent:
    """Base class for Bedrock-powered agents.
    
    Args:
        name (str): Name of the agent
        model_id (str): Bedrock model ID (e.g., anthropic.claude-v2)
        aws_config (AWSConfig): AWS configuration
        instructions (Optional[str]): System instructions for the agent
        temperature (Optional[float]): Temperature for model inference
        max_tokens (Optional[int]): Maximum tokens for model response
        
    Raises:
        InvalidModelError: If the model ID is not supported
        AWSConfigError: If there is an error with AWS configuration
    """
    
    def __init__(
        self,
        name: str,
        model_id: str,
        aws_config: AWSConfig,
        instructions: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ):
        self.name = name
        self.model_id = model_id
        self.instructions = instructions
        self.temperature = self._validate_temperature(temperature)
        self.max_tokens = max_tokens or 1000
        self._tools: Dict[str, BaseTool] = {}
        
        # Validate model ID
        self._validate_model_id()
        
        try:
            # Create a session with the profile
            session = boto3.Session(
                region_name=aws_config.region,
                profile_name=aws_config.profile
            )
            
            # Create the client using the session
            self.bedrock = session.client(
                'bedrock-runtime',
                endpoint_url=aws_config.endpoint_url
            )
            
            # Register built-in tools
            from ..tools.web import WebSearchTool
            if "WebSearchTool" not in ToolFactory._tool_types:
                ToolFactory.register_tool_type(WebSearchTool)
            
        except (BotoCoreError, ClientError) as e:
            raise AWSConfigError(f"Failed to initialize AWS client: {str(e)}")
    
    def _validate_model_id(self) -> None:
        """Validate the model ID.
        
        Raises:
            InvalidModelError: If the model ID is not supported
        """
        model_family = next((family for family in SUPPORTED_MODELS if self.model_id.startswith(family)), None)
        if not model_family:
            supported = ", ".join(SUPPORTED_MODELS.keys())
            raise InvalidModelError(
                f"Unsupported model family in '{self.model_id}'. "
                f"Supported families are: {supported}"
            )
        
        version = self.model_id[len(model_family)+1:]
        if version not in SUPPORTED_MODELS[model_family]["versions"]:
            versions = ", ".join(SUPPORTED_MODELS[model_family]["versions"])
            raise InvalidModelError(
                f"Unsupported version '{version}' for model family '{model_family}'. "
                f"Supported versions are: {versions}"
            )
    
    def _validate_temperature(self, temperature: Optional[float]) -> float:
        """Validate and return the temperature value.
        
        Args:
            temperature (Optional[float]): Temperature value to validate
            
        Returns:
            float: Validated temperature value
            
        Raises:
            ValueError: If temperature is invalid
        """
        if temperature is None:
            return 0.7
        if not 0 <= temperature <= 1:
            raise ValueError("Temperature must be between 0 and 1")
        return temperature
    
    @property
    def tools(self) -> List[BaseTool]:
        """Get all tools as a list.
        
        Returns:
            List[BaseTool]: List of all tools
        """
        return list(self._tools.values())
    
    def add_tool(self, tool: Union[BaseTool, str], **kwargs) -> BaseTool:
        """Add a tool to the agent.
        
        Args:
            tool (Union[BaseTool, str]): Tool instance or tool type name
            **kwargs: Tool configuration parameters if creating from type name
            
        Returns:
            BaseTool: Added tool instance
            
        Raises:
            ToolError: If tool creation fails or tool already exists
        """
        if isinstance(tool, str):
            # Create tool from type name
            tool = ToolFactory.create_tool(tool, **kwargs)
        elif not isinstance(tool, BaseTool):
            raise ToolError(f"Invalid tool type: {type(tool)}")
        
        # Add tool to collection
        self._tools[tool.name] = tool
        return tool
    
    def get_tool(self, tool_name: str) -> BaseTool:
        """Get a tool by name.
        
        Args:
            tool_name (str): Name of the tool to get
            
        Returns:
            BaseTool: Tool if found
            
        Raises:
            ToolError: If tool is not found
        """
        if tool_name not in self._tools:
            raise ToolError(f"Tool '{tool_name}' not found")
        return self._tools[tool_name]
    
    def get_tools(self) -> Dict[str, BaseTool]:
        """Get all tools.
        
        Returns:
            Dict[str, BaseTool]: Dictionary of tool name to tool instance
        """
        return self._tools.copy()
    
    def remove_tool(self, tool_name: str) -> None:
        """Remove a tool by name.
        
        Args:
            tool_name (str): Name of the tool to remove
            
        Raises:
            ToolError: If tool is not found
        """
        if tool_name not in self._tools:
            raise ToolError(f"Tool '{tool_name}' not found")
        del self._tools[tool_name]
    
    def clear_tools(self) -> None:
        """Remove all tools."""
        self._tools.clear()
    
    def _format_claude_prompt(self, message: str) -> str:
        """Format request for Claude models.
        
        Args:
            message (str): Message to format
            
        Returns:
            str: Formatted prompt
        """
        system = f"System: {self.instructions}\n\n" if self.instructions else ""
        return f"{system}Human: {message}\n\nAssistant:"
    
    def _format_titan_prompt(self, message: str) -> Dict[str, Any]:
        """Format request for Titan models."""
        system = f"System: {self.instructions}\n\n" if self.instructions else ""
        prompt = f"{system}Human: {message}\nAssistant:"
        
        return {
            "inputText": prompt,
            "textGenerationConfig": {
                "temperature": self.temperature,
                "maxTokenCount": self.max_tokens
            }
        }
    
    def _format_jurassic_prompt(self, message: str) -> Dict[str, Any]:
        """Format request for Jurassic models."""
        system = f"{self.instructions}\n\n" if self.instructions else ""
        prompt = f"{system}{message}"
        
        return {
            "prompt": prompt,
            "temperature": self.temperature,
            "maxTokens": self.max_tokens,
            "stopSequences": ["Human:", "Assistant:"]
        }
    
    def _format_cohere_prompt(self, message: str) -> Dict[str, Any]:
        """Format request for Cohere models."""
        system = f"{self.instructions}\n\n" if self.instructions else ""
        prompt = f"{system}{message}"
        
        return {
            "prompt": prompt,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "return_likelihoods": "NONE"
        }
    
    def _format_request_body(self, message: str) -> Dict[str, Any]:
        """Format request body based on model type.
        
        Args:
            message (str): Message to format
            
        Returns:
            Dict[str, Any]: Formatted request body
        """
        if self.model_id.startswith("anthropic.claude"):
            # Format for Claude models
            request_body = {
                "prompt": self._format_claude_prompt(message),
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "anthropic_version": "bedrock-2023-05-31"
            }
            
            # Add tool schema if tools are configured
            if self._tools:
                request_body["tools"] = [
                    tool.get_schema() for tool in self._tools.values()
                ]
            
        elif self.model_id.startswith("amazon.titan"):
            # Format for Titan models
            request_body = {
                "inputText": self._format_titan_prompt(message),
                "textGenerationConfig": {
                    "maxTokenCount": self.max_tokens,
                    "temperature": self.temperature,
                    "topP": 1
                }
            }
        elif self.model_id.startswith("ai21.j2"):
            # Format for Jurassic models
            request_body = self._format_jurassic_prompt(message)
        elif self.model_id.startswith("cohere.command"):
            # Format for Cohere models
            request_body = self._format_cohere_prompt(message)
        else:
            raise ValueError(f"Unsupported model type: {self.model_id}")
        
        return request_body
    
    def _parse_response(self, response: Dict[str, Any]) -> str:
        """Parse response based on model type.
        
        Args:
            response (Dict[str, Any]): Response from the model
            
        Returns:
            str: Parsed response text
            
        Raises:
            ResponseParsingError: If response cannot be parsed
        """
        try:
            if self.model_id.startswith("anthropic.claude"):
                if "completion" not in response:
                    raise ResponseParsingError("Missing 'completion' in response")
                return response["completion"]
            elif self.model_id.startswith("amazon.titan"):
                if "results" not in response or not response["results"]:
                    raise ResponseParsingError("Missing 'results' in response")
                if "outputText" not in response["results"][0]:
                    raise ResponseParsingError("Missing 'outputText' in response")
                return response["results"][0]["outputText"]
            elif self.model_id.startswith("ai21.j2"):
                if "completions" not in response or not response["completions"]:
                    raise ResponseParsingError("Missing 'completions' in response")
                if "data" not in response["completions"][0]:
                    raise ResponseParsingError("Missing 'data' in response")
                if "text" not in response["completions"][0]["data"]:
                    raise ResponseParsingError("Missing 'text' in response")
                return response["completions"][0]["data"]["text"]
            elif self.model_id.startswith("cohere.command"):
                if "generations" not in response or not response["generations"]:
                    raise ResponseParsingError("Missing 'generations' in response")
                if "text" not in response["generations"][0]:
                    raise ResponseParsingError("Missing 'text' in response")
                return response["generations"][0]["text"]
            else:
                # This should never happen due to _validate_model_id
                for key in ["completion", "text", "output", "response"]:
                    if key in response:
                        return response[key]
                raise ResponseParsingError(f"Unable to parse response: {response}")
        except (KeyError, IndexError, TypeError) as e:
            raise ResponseParsingError(
                f"Failed to parse response for model {self.model_id}: {str(e)}\n"
                f"Response: {response}"
            )
    
    def _get_tool_schemas(self) -> List[Dict[str, Any]]:
        """Get schemas for all tools."""
        return [tool.get_schema() for tool in self._tools.values()]
    
    async def _execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> str:
        """Execute a tool by name.
        
        Args:
            tool_name (str): Name of the tool to execute
            parameters (Dict[str, Any]): Tool parameters
            
        Returns:
            str: Tool execution result
            
        Raises:
            ToolNotFoundError: If tool is not found
            ToolExecutionError: If tool execution fails
        """
        if tool_name not in self._tools:
            raise ToolNotFoundError(f"Tool '{tool_name}' not found")
        
        try:
            return await self._tools[tool_name].execute(**parameters)
        except Exception as e:
            raise ToolExecutionError(f"Failed to execute tool '{tool_name}': {str(e)}")
    
    async def process_message(self, message: str) -> str:
        """Process a message and return the response.
        
        Args:
            message (str): Message to process
            
        Returns:
            str: Response from the model
        """
        # Format request body based on model type
        request_body = self._format_request_body(message)
        
        # Invoke model
        response = await self._invoke_model(request_body)
        
        # Parse response based on model type
        if self.model_id.startswith("anthropic.claude"):
            # Extract tool calls if present
            tool_calls = self._extract_tool_calls(response)
            
            # Execute tool calls if present
            if tool_calls:
                for tool_call in tool_calls:
                    await self._execute_tool_call(tool_call)
        
        return self._extract_response_text(response)
    
    async def _invoke_model(self, request_body: Dict[str, Any]) -> Dict[str, Any]:
        """Invoke the Bedrock model.
        
        Args:
            request_body (Dict[str, Any]): Request body for the model
            
        Returns:
            Dict[str, Any]: Model response
            
        Raises:
            ModelInvokeError: If model invocation fails
            ResponseParsingError: If response cannot be parsed
            ToolExecutionError: If tool execution fails
            ToolNotFoundError: If a tool is not found
        """
        try:
            # Invoke the model
            response = self.bedrock.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body)
            )
            
            # Parse response
            response_body = json.loads(response["body"].read())
            
            return response_body
            
        except (BotoCoreError, ClientError) as e:
            raise ModelInvokeError(f"Failed to invoke model: {str(e)}")
        except json.JSONDecodeError as e:
            raise ResponseParsingError(f"Failed to decode response: {str(e)}")
    
    def _extract_tool_calls(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract tool calls from the model response.
        
        Args:
            response (Dict[str, Any]): Model response
            
        Returns:
            List[Dict[str, Any]]: List of tool calls
        """
        if self.model_id.startswith("anthropic.claude"):
            if "tool_calls" in response:
                return response["tool_calls"]
        return []
    
    async def _execute_tool_call(self, tool_call: Dict[str, Any]) -> str:
        """Execute a tool call.
        
        Args:
            tool_call (Dict[str, Any]): Tool call to execute
            
        Returns:
            str: Tool execution result
            
        Raises:
            ToolNotFoundError: If tool is not found
            ToolExecutionError: If tool execution fails
        """
        if "function" not in tool_call:
            raise ToolExecutionError("Missing 'function' in tool call")
        
        func = tool_call["function"]
        return await self._execute_tool(func["name"], json.loads(func["arguments"]))
    
    def _extract_response_text(self, response: Dict[str, Any]) -> str:
        """Extract response text from the model response.
        
        Args:
            response (Dict[str, Any]): Model response
            
        Returns:
            str: Extracted response text
        """
        if self.model_id.startswith("anthropic.claude"):
            return self._parse_response(response)
        elif self.model_id.startswith("amazon.titan"):
            return self._parse_response(response)
        elif self.model_id.startswith("ai21.j2"):
            return self._parse_response(response)
        elif self.model_id.startswith("cohere.command"):
            return self._parse_response(response)
        else:
            # This should never happen due to _validate_model_id
            for key in ["completion", "text", "output", "response"]:
                if key in response:
                    return response[key]
            raise ResponseParsingError(f"Unable to parse response: {response}") 