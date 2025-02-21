"""Module for implementing Bedrock-powered agents.

This module provides a flexible architecture for supporting multiple Bedrock models.
"""

import json
import logging
from datetime import datetime
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

    Each agent has:
    1. A specific role/domain of expertise
    2. A set of tools it can use
    3. A memory system for context
    4. A Bedrock model for processing
    """

    def __init__(
        self,
        model_id: str,
        name: str,
        role: str,
        tools: Optional[List[BaseTool]] = None,
        memory: Optional[BaseMemory] = None,
        system_prompt: Optional[str] = None,
    ) -> None:
        """Initialize the agent.

        Args:
            model_id: Bedrock model ID
            name: Name of the agent
            role: Description of agent's role/expertise
            tools: Optional list of tools available to the agent
            memory: Optional memory system (defaults to SimpleMemory)
            system_prompt: Optional system prompt

        Raises:
            InvalidModelError: If model ID is not supported
        """
        self.model_id = model_id
        self.name = name
        self.role = role
        self.tools = {tool.name: tool for tool in tools} if tools else {}
        self.memory = memory or SimpleMemory()
        self.system_prompt = system_prompt

        logger.debug(f"Initializing agent {name} with role: {role}")
        logger.debug(f"Available tools: {list(self.tools.keys())}")

        # Initialize AWS session
        self.session = boto3.Session(
            region_name=AWSConfig.region,
            profile_name=AWSConfig.profile,
        )

        # Initialize model
        self.model = self._initialize_model()

    def _initialize_model(self) -> BedrockModel:
        """Initialize the Bedrock model."""
        try:
            return ModelFactory.create_model(self.model_id)
        except ValueError as e:
            raise InvalidModelError(str(e))

    def _build_prompt(self, message: str) -> str:
        """Build the complete prompt including context and conversation history.

        This method builds a comprehensive prompt that includes:
        1. System prompt and role context
        2. Available tools and their schemas
        3. Recent conversation history
        4. Response format instructions
        5. Current message
        """
        prompt = []

        # Add system prompt if provided
        if self.system_prompt:
            prompt.append(f"System: {self.system_prompt}")

        # Add role context
        prompt.append(f"You are a specialized agent with expertise in: {self.role}")

        # Add available tools
        if self.tools:
            prompt.append("\n<tools>")
            for tool in self.tools.values():
                prompt.append(f"- {tool.name}: {tool.description}")
                schema = tool.get_schema()
                prompt.append(f"  Schema: {json.dumps(schema, indent=2)}")
            prompt.append("</tools>")

        # Add conversation history from memory
        recent_messages = self.memory.get_messages()[-5:]  # Get last 5 messages
        if recent_messages:
            prompt.append("\n<conversation_history>")
            for msg in recent_messages:
                # Include metadata about tool usage if available
                tool_info = ""
                if msg.metadata and msg.metadata.get("type") == "tool_result":
                    tool_info = (
                        f" [Tool Result: {msg.metadata.get('tool_call_id', 'unknown')}]"
                    )
                prompt.append(f"{msg.role}{tool_info}: {msg.content}")
            prompt.append("</conversation_history>")

        # Add response format instructions using XML
        prompt.extend(
            [
                "\n<response_format>",
                "You must respond in one of two formats:",
                "\n1. To use a tool:",
                "Respond with ONLY a JSON object in this exact format (no explanation text outside the JSON):",
                '{"type": "tool_call", "tool_calls": [{"id": "call_1", "type": "function", "function": {"name": "tool_name", "arguments": {"arg1": "value1"}}}]}',
                "\n2. For normal responses:",
                "Respond with ONLY a JSON object in this exact format (no explanation text outside the JSON):",
                '{"type": "message", "content": "your natural language response here"}',
                "\n<rules>",
                "- Always use proper JSON with double quotes",
                "- Never include explanations or text outside the JSON object",
                "- Tool arguments must be a valid JSON object, not a string",
                "- Respond with exactly one complete JSON object",
                "- Maintain conversation context from history",
                "- Reference previous tool results when relevant",
                "</rules>",
                "</response_format>",
                f"\n<input>{message}</input>",
            ]
        )

        final_prompt = "\n".join(prompt)
        logger.debug(f"Built prompt for agent {self.name}:\n{final_prompt}")
        return final_prompt

    def generate(self, message: str) -> AgentResponse:
        """Generate a response to a message.

        This method:
        1. Records the incoming message in memory
        2. Generates a response using the model
        3. Records the response and any tool calls in memory
        4. Returns the processed response

        Args:
            message: Message to respond to

        Returns:
            Response containing either tool calls or direct message
        """
        logger.debug(f"Agent {self.name} generating response for message: {message}")

        # Record incoming message in memory
        self.memory.add_message(
            Message(
                role="user",
                content=message,
                timestamp=datetime.now(),
                metadata={"type": "user_message", "agent": self.name},
            )
        )

        # Get bedrock client
        client = self.session.client(
            "bedrock-runtime",
            endpoint_url=AWSConfig.endpoint_url,
        )

        # Build prompt and get response
        prompt = self._build_prompt(message)
        response = self.model.invoke(client=client, message=prompt)
        logger.debug(f"Raw model response: {response}")

        # Record the response in memory with appropriate metadata
        if response.get("type") == "tool_call":
            # Record tool call intent
            self.memory.add_message(
                Message(
                    role="assistant",
                    content=json.dumps(response["tool_calls"]),
                    timestamp=datetime.now(),
                    metadata={
                        "type": "tool_call_intent",
                        "agent": self.name,
                        "tool_calls": response["tool_calls"],
                    },
                )
            )
        else:
            # Record normal message response
            self.memory.add_message(
                Message(
                    role="assistant",
                    content=response.get("content", ""),
                    timestamp=datetime.now(),
                    metadata={"type": "assistant_response", "agent": self.name},
                )
            )

        # Return the processed response
        return response

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
