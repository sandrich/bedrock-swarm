"""Module for implementing Bedrock-powered agents.

This module provides a flexible architecture for supporting multiple Bedrock models.
"""

import json
import logging
from typing import List, Optional

import boto3

from ..config import AWSConfig
from ..exceptions import InvalidModelError
from ..memory.base import BaseMemory, Message, SimpleMemory
from ..models.base import BedrockModel
from ..models.factory import ModelFactory
from ..tools.base import BaseTool
from ..types import AgentResponse

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
        aws_config = AWSConfig(region="us-west-2")  # Default to us-west-2
        self.session = boto3.Session(
            region_name=aws_config.region,
            profile_name=aws_config.profile,
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
        prompt = []

        # Start with system prompt if provided
        if self.system_prompt:
            prompt.append(self.system_prompt)
            prompt.append("")  # Add blank line after system prompt

        # Add tool instructions
        prompt.append("You have access to the following tools:")

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
                '   {"type": "tool_call", "tool_calls": [{"id": "call_xxx", "type": "function", "function": {"name": "tool_name", "arguments": "{\\"steps\\":[{\\"step_number\\":1}]}"}}]}',
                "",
                "2. The arguments field MUST be a JSON string with escaped quotes. For example:",
                '   CORRECT: {"type": "tool_call", "tool_calls": [{"id": "call_1", "type": "function", "function": {"name": "create_plan", "arguments": "{\\"steps\\":[{\\"step_number\\":1,\\"description\\":\\"Calculate 2 + 2\\",\\"specialist\\":\\"calculator\\"}],\\"final_output_format\\":\\"Result: {X}\\"}"}}]}',
                "",
                "3. For a normal response without tools, respond with:",
                '   {"type": "message", "content": "your response here"}',
                "",
                "4. Do not include ANY other text before or after the JSON.",
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

        # Build complete prompt including system prompt and tool instructions
        complete_prompt = self._build_tool_prompt(message)
        response = self.model.invoke(
            client=client,
            message=complete_prompt,
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
