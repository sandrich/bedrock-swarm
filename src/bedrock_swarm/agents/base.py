"""Module for implementing Bedrock-powered agents.

This module provides a flexible architecture for supporting multiple Bedrock models.
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4

import boto3
from botocore.exceptions import ClientError

from ..config import AWSConfig
from ..exceptions import (
    InvalidModelError,
    ModelInvokeError,
    ResponseParsingError,
    ToolError,
    ToolExecutionError,
    ToolNotFoundError,
)
from ..memory.base import BaseMemory, Message, SimpleMemory
from ..models.base import BedrockModel
from ..models.factory import ModelFactory
from ..tools.base import BaseTool
from ..types import AgentResponse, ToolCall

# Configure logger
logger = logging.getLogger(__name__)


class BedrockAgent:
    """Base class for Bedrock-powered agents.

    This class provides a flexible architecture for working with different
    Bedrock models. It supports features like streaming responses, tool/function calling,
    and memory management depending on the model's capabilities.

    Args:
        model_id: Bedrock model ID (must be one of the supported models)
        name: Name of the agent
        tools: Optional list of tools available to the agent
        memory: Optional memory system (defaults to SimpleMemory)
        system_prompt: Optional system prompt

    Raises:
        InvalidModelError: If the model ID is not supported
        AWSConfigError: If there is an error with AWS configuration
    """

    def __init__(
        self,
        model_id: str,
        name: str,
        tools: Optional[List[BaseTool]] = None,
        memory: Optional[BaseMemory] = None,
        system_prompt: Optional[str] = None,
    ) -> None:
        """Initialize the agent.

        Args:
            model_id: Bedrock model ID (must be one of the supported models)
            name: Name of the agent
            tools: Optional list of tools available to the agent
            memory: Optional memory system (defaults to SimpleMemory)
            system_prompt: Optional system prompt

        Raises:
            InvalidModelError: If the model ID is not supported
            AWSConfigError: If there is an error with AWS configuration
        """
        self.model_id = model_id
        self.name = name
        self.tools = {tool.name: tool for tool in tools} if tools else {}
        self.memory = memory or SimpleMemory()
        self.system_prompt = system_prompt

        # Initialize AWS session
        self.session = boto3.Session(
            region_name=AWSConfig.region,
            profile_name=AWSConfig.profile,
        )

        # Initialize model using factory
        self.model = self._initialize_model()

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

    def _build_tool_prompt(self, message: str) -> str:
        """Build the tool prompt based on registered tools.

        Args:
            message: User's query

        Returns:
            Complete prompt including tool descriptions
        """
        # Start with base prompt
        prompt = ["You are a helpful assistant with access to the following tools:"]

        # Add each tool's description and parameters
        for tool in self.tools.values():
            schema = tool.get_schema()
            prompt.extend(
                [f"\n{schema['name']}: {schema['description']}", "Parameters:"]
            )

            # Add parameters
            params = schema["parameters"].get("properties", {})
            required = schema["parameters"].get("required", [])
            for param_name, param_info in params.items():
                req = "(required)" if param_name in required else "(optional)"
                prompt.append(
                    f"- {param_name}: {param_info.get('description', '')} {req}"
                )

        # Add instructions for tool usage
        prompt.extend(
            [
                "\nCRITICAL INSTRUCTIONS:",
                "1. To use a tool, your ENTIRE response must be ONLY the JSON:",
                '   {"type": "tool_call", "tool_calls": [{"id": "call_xxx", "type": "function", "function": {"name": "tool_name", "arguments": "{...}"}}]}',
                "",
                "2. For a normal response without tools, respond with:",
                '   {"type": "message", "content": "your response here"}',
                "",
                "3. Do not include ANY other text before or after the JSON.",
                "",
                f"User query: {message}",
            ]
        )

        return "\n".join(prompt)

    def generate(self, message: str) -> AgentResponse:
        """Generate a response to a message.

        This method:
        1. Asks model if it needs to use a tool
        2. Returns either a tool call or direct response

        Args:
            message: Message to respond to

        Returns:
            Response containing either tool calls or direct message
        """
        # Get bedrock client
        client = self.session.client(
            "bedrock-runtime",
            endpoint_url=AWSConfig.endpoint_url,
        )

        # Ask model if it needs to do a tool call
        tool_prompt = self._build_tool_prompt(message)
        response = self.model.invoke(
            client=client,
            message=tool_prompt,
        )

        # Parse response
        try:
            content = response["content"].strip()
            if content.startswith("{") and content.endswith("}"):
                return json.loads(content)
        except json.JSONDecodeError:
            pass

        # Return as message response if not a valid tool call
        return {"type": "message", "content": response["content"], "tool_calls": None}

    def _format_prompt(self, message: str, history: List[Message]) -> str:
        """Format the prompt with message history.

        Args:
            message: Current message
            history: Message history

        Returns:
            Formatted prompt string
        """
        # Start with system prompt if provided
        prompt = f"{self.system_prompt}\n\n" if self.system_prompt else ""

        # Add message history
        for msg in history:
            prompt += f"{msg.role}: {msg.content}\n"

        # Add current message
        prompt += f"human: {message}\nassistant:"

        return prompt

    @property
    def last_token_count(self) -> int:
        """Get the token count from the last request.

        Returns:
            int: Number of tokens used in last request
        """
        return getattr(self, "_last_token_count", 0)
