"""Module for implementing Bedrock-powered agents.

This module provides a flexible architecture for supporting multiple Bedrock models.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import boto3
from botocore.exceptions import ClientError

from ..config import AWSConfig
from ..exceptions import (
    InvalidModelError,
    ModelInvokeError,
    ToolError,
    ToolExecutionError,
    ToolNotFoundError,
)
from ..memory.base import BaseMemory, Message, SimpleMemory
from ..models.base import BedrockModel
from ..models.factory import ModelFactory
from ..tools.base import BaseTool
from ..tools.factory import ToolFactory

# Configure logger
logger = logging.getLogger(__name__)


class BedrockAgent:
    """Base class for Bedrock-powered agents.

    This class provides a flexible architecture for working with different
    Bedrock models. It supports features like streaming responses, tool/function calling,
    and memory management depending on the model's capabilities.

    Args:
        name (str): Name of the agent
        model_id (str): Bedrock model ID (must be one of the supported models)
        aws_config (AWSConfig): AWS configuration
        instructions (Optional[str]): System instructions for the agent
        temperature (Optional[float]): Temperature for model inference (0-1)
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
            model_id (str): Bedrock model ID (must be one of the supported models)
            aws_config (AWSConfig): AWS configuration
            instructions (Optional[str]): System instructions for the agent
            temperature (Optional[float]): Temperature for model inference (0-1)
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
        self._tools: Dict[str, BaseTool] = {}
        self.aws_config = aws_config
        self.memory = memory or SimpleMemory()

        # Initialize AWS session
        self.session = boto3.Session(
            region_name=aws_config.region,
            profile_name=aws_config.profile,
        )

        # Initialize model
        self.model = self._initialize_model()
        self.max_tokens = max_tokens or self.model.get_default_max_tokens()

    def _validate_model_id(self) -> None:
        """Validate the model ID.

        Raises:
            InvalidModelError: If the model ID is not supported
        """
        try:
            # Attempt to create model - this will validate the ID
            ModelFactory.create_model(self.model_id)
        except ValueError as e:
            raise InvalidModelError(str(e))

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

    def _initialize_model(self) -> BedrockModel:
        """Initialize the appropriate model implementation.

        Returns:
            BedrockModel: Initialized model instance

        Raises:
            InvalidModelError: If the model ID is not supported
        """
        try:
            return ModelFactory.create_model(self.model_id)
        except ValueError as e:
            raise InvalidModelError(str(e))

    def process_message(
        self, message: str, tool_results: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """Process a message using the model.

        Args:
            message (str): Message to process
            tool_results (Optional[List[Dict[str, Any]]]): Results from previous tool calls

        Returns:
            str: Model's response

        Raises:
            ModelInvokeError: If there is an error invoking the model
        """
        # Format system instructions and tools
        system = self.instructions or ""
        tools = None
        if self._tools and self.model.supports_tools():
            tools = [tool.get_schema() for tool in self._tools.values()]

        # Get bedrock client
        client = self.session.client(
            "bedrock-runtime", endpoint_url=self.aws_config.endpoint_url
        )

        try:
            # Process message using model implementation
            response = self.model.process_message(
                client=client,
                message=message,
                system=system,
                tools=tools,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                tool_map=self._tools,
            )

            # Store token count from model
            self._last_token_count = self.model.last_token_count

            # Update memory
            if self.memory:
                self.memory.add_message(
                    Message(role="human", content=message, timestamp=datetime.now())
                )
                self.memory.add_message(
                    Message(
                        role="assistant", content=response, timestamp=datetime.now()
                    )
                )

            return response

        except ClientError as e:
            logger.error(f"Error processing message: {e}")
            raise ModelInvokeError(str(e)) from e
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            raise ModelInvokeError(str(e)) from e

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
        response_text = self.process_message(message)
        return {"response": response_text}

    @property
    def last_token_count(self) -> int:
        """Get the token count from the last request.

        Returns:
            int: Number of tokens used in last request
        """
        return getattr(self, "_last_token_count", 0)
