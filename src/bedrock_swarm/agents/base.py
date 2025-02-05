"""Module for implementing Bedrock-powered agents."""

import json
import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from ..config import AWSConfig
from ..exceptions import (
    AWSConfigError,
    InvalidModelError,
    ModelInvokeError,
    ResponseParsingError,
    ToolError,
    ToolExecutionError,
    ToolNotFoundError,
)
from ..memory.base import BaseMemory, Message, SimpleMemory
from ..tools.base import BaseTool
from ..tools.factory import ToolFactory

# Configure logger
logger = logging.getLogger(__name__)

# List of supported model families
SUPPORTED_MODELS = {
    "anthropic.claude": {"versions": ["v1", "v2", "v2:1", "instant-v1"]},
    "us.anthropic.claude-3-5-sonnet": {
        "versions": ["20241022-v2:0"]
    },  # Claude 3.5 Sonnet v2
    "amazon.titan": {"versions": ["text-express-v1", "text-lite-v1"]},
    "ai21.j2": {"versions": ["mid-v1", "ultra-v1"]},
    "cohere.command": {"versions": ["text-v14"]},
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
        memory (Optional[BaseMemory]): Memory system for the agent

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
        max_tokens: Optional[int] = None,
        memory: Optional[BaseMemory] = None,
    ) -> None:
        """Initialize a Bedrock agent.

        Args:
            name (str): Name of the agent
            model_id (str): Bedrock model ID (e.g., anthropic.claude-v2)
            aws_config (AWSConfig): AWS configuration
            instructions (Optional[str]): System instructions for the agent
            temperature (Optional[float]): Temperature for model inference
            max_tokens (Optional[int]): Maximum tokens for model response
            memory (Optional[BaseMemory]): Memory system for the agent

        Raises:
            InvalidModelError: If the model ID is not supported
            AWSConfigError: If there is an error with AWS configuration
        """
        self.name = name
        self.model_id = model_id
        self.instructions = instructions
        self.temperature = self._validate_temperature(temperature)
        self.max_tokens = max_tokens or 1000
        self._tools: Dict[str, BaseTool] = {}
        self.aws_config = aws_config
        self.memory = memory or SimpleMemory()
        self._last_token_count = 0

        # Initialize AWS session
        self.session = boto3.Session(
            region_name=aws_config.region,
            profile_name=aws_config.profile,
        )

        # Validate model ID
        self._validate_model_id()

        # Register built-in tools
        from ..tools.web import WebSearchTool

        if "WebSearchTool" not in ToolFactory._tool_types:
            ToolFactory.register_tool_type(WebSearchTool)

    def _validate_model_id(self) -> None:
        """Validate the model ID.

        Raises:
            InvalidModelError: If the model ID is not supported
        """
        # Special handling for Claude 3.5 models which have a different format
        if self.model_id.startswith("us.anthropic.claude-3-5"):
            model_family = "us.anthropic.claude-3-5-sonnet"
            version = self.model_id[len("us.anthropic.claude-3-5-sonnet-") :]
        else:
            model_family = next(
                (
                    family
                    for family in SUPPORTED_MODELS
                    if self.model_id.startswith(family)
                ),
                "",
            )
            if not model_family:
                supported = ", ".join(SUPPORTED_MODELS.keys())
                msg = (
                    "Unsupported model family '"
                    + self.model_id
                    + "'. Supported families are: "
                    + supported
                )
                raise InvalidModelError(msg)
            version = self.model_id[len(model_family) + 1 :]

        if version not in SUPPORTED_MODELS[model_family]["versions"]:
            versions = ", ".join(SUPPORTED_MODELS[model_family]["versions"])
            msg = (
                "Unsupported version '"
                + version
                + "' for model family '"
                + model_family
                + "'. Supported versions are: "
                + versions
            )
            raise InvalidModelError(msg)

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

    def add_tool(self, tool: Union[BaseTool, str], **kwargs: Any) -> BaseTool:
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
                "maxTokenCount": self.max_tokens,
            },
        }

    def _format_jurassic_prompt(self, message: str) -> Dict[str, Any]:
        """Format request for Jurassic models."""
        system = f"{self.instructions}\n\n" if self.instructions else ""
        prompt = f"{system}{message}"

        return {
            "prompt": prompt,
            "temperature": self.temperature,
            "maxTokens": self.max_tokens,
            "stopSequences": ["Human:", "Assistant:"],
        }

    def _format_cohere_prompt(self, message: str) -> Dict[str, Any]:
        """Format request for Cohere models."""
        system = f"{self.instructions}\n\n" if self.instructions else ""
        prompt = f"{system}{message}"

        return {
            "prompt": prompt,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "return_likelihoods": "NONE",
        }

    def _format_request_body(self, message: str) -> Dict[str, Any]:
        """Format request body based on model type.

        Args:
            message (str): Message to format

        Returns:
            Dict[str, Any]: Formatted request body
        """
        if self.model_id.startswith("us.anthropic.claude-3"):
            # Format for Claude 3.5 models
            system = ""
            if self.instructions:
                system = self.instructions

            # Add function calling capability
            if self._tools:
                if system:
                    system += "\n\n"
                system += "You have access to these functions:\n\n"
                for tool in self._tools.values():
                    schema = tool.get_schema()
                    system += "<function>\n"
                    system += f"name: {schema['name']}\n"
                    system += f"description: {schema['description']}\n"
                    system += "parameters:\n"
                    for param_name, param in schema["parameters"]["properties"].items():
                        required = param_name in schema["parameters"].get(
                            "required", []
                        )
                        system += f"  - {param_name} ({'required' if required else 'optional'}): {param['description']}\n"
                    system += "</function>\n\n"

                system += """To call a function:
1. Output exactly one JSON object in this format:
{
    "function": "function_name",
    "parameters": {
        "param1": "value1",
        "param2": "value2"
    }
}
2. Wait for the function result
3. Continue your response based on the result

You must output valid JSON when calling functions. Do not include any other text or explanation when making the function call."""

            return {
                "anthropic_version": "bedrock-2023-05-31",
                "messages": [{"role": "user", "content": message}],
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "system": system,
            }

        elif self.model_id.startswith("anthropic.claude"):
            # Format for older Claude models
            system = f"{self.instructions}\n\n" if self.instructions else ""

            # Add function calling capability
            if self._tools:
                system += "\nYou have access to these functions:\n\n"
                for tool in self._tools.values():
                    schema = tool.get_schema()
                    system += "<function>\n"
                    system += f"name: {schema['name']}\n"
                    system += f"description: {schema['description']}\n"
                    system += "parameters:\n"
                    for param_name, param in schema["parameters"]["properties"].items():
                        required = param_name in schema["parameters"].get(
                            "required", []
                        )
                        system += f"  - {param_name} ({'required' if required else 'optional'}): {param['description']}\n"
                    system += "</function>\n\n"

                system += """
To call a function:
1. Output exactly one JSON object in this format:
{
    "function": "function_name",
    "parameters": {
        "param1": "value1",
        "param2": "value2"
    }
}
2. Wait for the function result
3. Continue your response based on the result

You must output valid JSON when calling functions. Do not include any other text or explanation when making the function call.
"""

            return {
                "prompt": f"{system}Human: {message}\n\nAssistant:",
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "anthropic_version": "bedrock-2023-05-31",
            }

        elif self.model_id.startswith("amazon.titan"):
            # Format for Titan models
            return {
                "inputText": self._format_titan_prompt(message),
                "textGenerationConfig": {
                    "maxTokenCount": self.max_tokens,
                    "temperature": self.temperature,
                    "topP": 1,
                },
            }
        elif self.model_id.startswith("ai21.j2"):
            # Format for Jurassic models
            return self._format_jurassic_prompt(message)
        elif self.model_id.startswith("cohere.command"):
            # Format for Cohere models
            return self._format_cohere_prompt(message)
        else:
            raise ValueError(f"Unsupported model type: {self.model_id}")

    def _get_response_text(self, response: Dict[str, Any]) -> str:
        """Extract response text from model response.

        Args:
            response (Dict[str, Any]): Raw model response

        Returns:
            str: Extracted response text

        Raises:
            ResponseParsingError: If response cannot be parsed
        """
        try:
            if self.model_id.startswith("anthropic.claude"):
                return response.get("completion", "")
            elif self.model_id.startswith("us.anthropic.claude-3"):
                return response.get("completion", "")
            elif self.model_id.startswith("amazon.titan"):
                return response.get("results", [{}])[0].get("outputText", "")
            elif self.model_id.startswith("ai21.j2"):
                return (
                    response.get("completions", [{}])[0].get("data", {}).get("text", "")
                )
            elif self.model_id.startswith("cohere.command"):
                return response.get("generations", [{}])[0].get("text", "")
            else:
                raise ResponseParsingError(f"Unsupported model: {self.model_id}")
        except (KeyError, IndexError) as e:
            raise ResponseParsingError(f"Failed to parse response: {str(e)}")

    def _execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> str:
        """Execute a tool by name with parameters.

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
            return self._tools[tool_name].execute(**parameters)
        except Exception as e:
            raise ToolExecutionError(f"Failed to execute tool '{tool_name}': {str(e)}")

    def process_message(
        self, message: str, tool_results: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """Process a message and return the model's response.

        Args:
            message (str): Message to process
            tool_results (Optional[List[Dict[str, Any]]]): Results from previous tool calls

        Returns:
            str: Model response

        Raises:
            ModelInvokeError: If model invocation fails
            ResponseParsingError: If response cannot be parsed
            ToolExecutionError: If tool execution fails
            ToolNotFoundError: If tool is not found
        """
        # Initialize token count
        self._last_token_count = 0

        # Add user message to memory
        self.memory.add_message(
            Message(role="human", content=message, timestamp=datetime.now())
        )

        # Format request body
        request_body = self._format_request_body(message)

        # Process message and get response
        response = self._invoke_model(request_body)

        # Update token count
        if "usage" in response:
            self._last_token_count = response["usage"].get("total_tokens", 0)

        # Extract response text
        response_text = self._get_response_text(response)

        # Add assistant response to memory
        self.memory.add_message(
            Message(role="assistant", content=response_text, timestamp=datetime.now())
        )

        return response_text

    def _invoke_model(self, request_body: Dict[str, Any]) -> Dict[str, Any]:
        """Invoke the Bedrock model."""
        if not self.session:
            raise AWSConfigError("AWS session not initialized")

        logger.debug("Starting model invocation")
        logger.debug("Session object: %s", self.session)

        try:
            logger.debug(
                "Creating Bedrock client with config: region=%s, profile=%s",
                self.aws_config.region,
                self.aws_config.profile,
            )
            if self.aws_config.endpoint_url:
                logger.debug(
                    "Using custom endpoint URL: %s", self.aws_config.endpoint_url
                )

            logger.debug("Creating client...")
            bedrock = self.session.client(
                "bedrock-runtime", endpoint_url=self.aws_config.endpoint_url
            )
            logger.debug("Client created: %s", bedrock)

            try:
                logger.debug("Invoking model: %s", self.model_id)
                logger.debug("Request body: %s", json.dumps(request_body, indent=2))

                if self.model_id.startswith("us.anthropic.claude-3"):
                    logger.debug("Using streaming response for Claude 3.5")
                    # Use invoke_model_with_response_stream for Claude 3.5
                    response = bedrock.invoke_model_with_response_stream(
                        modelId=self.model_id, body=json.dumps(request_body)
                    )
                    logger.debug("Got streaming response: %s", response)

                    # Read the streaming response
                    response_body = {"completion": ""}
                    stream = response.get("body")
                    logger.debug("Stream object: %s", stream)

                    if not stream:
                        raise ModelInvokeError("No response stream received from model")

                    for event in stream:
                        chunk = event.get("chunk", {}).get("bytes")
                        if not chunk:
                            continue

                        try:
                            chunk_data = json.loads(chunk.decode())
                            logger.debug("Received chunk: %s", chunk_data)

                            if chunk_data.get("type") == "content_block_delta":
                                delta = chunk_data.get("delta", {}).get("text", "")
                                response_body["completion"] += delta

                        except json.JSONDecodeError as e:
                            logger.error("Error decoding chunk: %s", e)
                            raise ResponseParsingError(f"Invalid chunk format: {e}")

                    stream.close()
                    return response_body

                else:
                    # Use standard invoke_model for other models
                    response = bedrock.invoke_model(
                        modelId=self.model_id,
                        body=json.dumps(request_body),
                    )
                    logger.debug("Got response: %s", response)

                    response_body = response.get("body")
                    if not response_body:
                        raise ModelInvokeError("Empty response from model")

                    try:
                        return json.loads(response_body.read())
                    except json.JSONDecodeError as e:
                        raise ResponseParsingError(f"Invalid response format: {e}")

            except ClientError as e:
                logger.error("AWS client error: %s", e)
                raise ModelInvokeError(f"Error invoking model: {e}")

        except BotoCoreError as e:
            logger.error("AWS configuration error: %s", e)
            raise AWSConfigError(f"Error creating AWS client: {e}")

    def _extract_tool_calls(self, response: str) -> List[Dict[str, Any]]:
        """Extract tool calls from the response.

        Args:
            response (str): Raw response from the model

        Returns:
            List[Dict[str, Any]]: List of tool calls
        """
        # Try to find tool calls in XML blocks
        pattern = r"<tool_calls>(.*?)</tool_calls>"
        matches = re.findall(pattern, response, flags=re.DOTALL)
        if not matches:
            return []

        try:
            # Try to parse as JSON
            tool_calls = json.loads(matches[0])
            if isinstance(tool_calls, list):
                return tool_calls
            return []
        except json.JSONDecodeError:
            return []

    def _execute_tool_call(self, tool_call: Dict[str, Any]) -> str:
        """Execute a tool call from Claude 3.5.

        Args:
            tool_call (Dict[str, Any]): Tool call information

        Returns:
            str: Tool execution result

        Raises:
            ToolNotFoundError: If tool is not found
            ToolExecutionError: If tool execution fails
        """
        if tool_call["type"] != "function":
            raise ToolExecutionError(f"Unsupported tool call type: {tool_call['type']}")

        tool_name = tool_call["function"]["name"]
        parameters = json.loads(tool_call["function"]["arguments"])
        return self._execute_tool(tool_name, parameters)

    def generate(
        self, message: str, tool_results: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, str]:
        """Generate a response to a message.

        Args:
            message (str): Message to process
            tool_results (Optional[List[Dict[str, Any]]]): Results from previous tool calls

        Returns:
            Dict[str, str]: Response containing the model's output

        Raises:
            ModelInvokeError: If model invocation fails
            ResponseParsingError: If response cannot be parsed
            ToolExecutionError: If tool execution fails
            ToolNotFoundError: If tool is not found
        """
        response_text = self.process_message(message, tool_results)
        return {"response": response_text}

    @property
    def last_token_count(self) -> int:
        """Get the token count from the last request.

        Returns:
            int: Number of tokens used in last request
        """
        return getattr(self, "_last_token_count", 0)
