"""Base class for Bedrock model implementations."""

import json
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from botocore.client import BaseClient

from ..tools.base import BaseTool


class BedrockModel(ABC):
    """Base class for Bedrock model implementations.

    This class defines the interface that all model implementations must follow.
    Each model implementation should handle its own request formatting, response
    parsing, and tool/function call handling.
    """

    def __init__(self) -> None:
        """Initialize the model."""
        self.last_token_count = 0

    @abstractmethod
    def get_default_max_tokens(self) -> int:
        """Get the default maximum tokens for this model.

        Returns:
            int: Default maximum tokens
        """
        pass

    @abstractmethod
    def supports_tools(self) -> bool:
        """Check if this model supports tools/function calling.

        Returns:
            bool: True if tools are supported
        """
        pass

    @abstractmethod
    def supports_streaming(self) -> bool:
        """Check if this model supports streaming responses.

        Returns:
            bool: True if streaming is supported
        """
        pass

    @abstractmethod
    def process_message(
        self,
        client: BaseClient,
        message: str,
        system: str,
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        tool_map: Optional[Dict[str, BaseTool]] = None,
    ) -> str:
        """Process a message using this model.

        This method handles the complete lifecycle of processing a message:
        1. Format the request for this model
        2. Invoke the model (streaming or non-streaming)
        3. Parse the response
        4. Handle any tool/function calls
        5. Return the final response

        Args:
            client: Bedrock runtime client
            message: Message to process
            system: System instructions
            tools: List of tool schemas
            temperature: Temperature for model inference
            max_tokens: Maximum tokens for response
            tool_map: Map of tool names to tool instances

        Returns:
            str: Model's response

        Raises:
            ModelInvokeError: If there is an error invoking the model
            ResponseParsingError: If there is an error parsing the response
            ToolExecutionError: If there is an error executing a tool
        """
        pass

    @abstractmethod
    def format_request(
        self,
        message: str,
        system: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> Dict[str, Any]:
        """Format a request for the model.

        Args:
            message: The message to send
            system: Optional system instructions
            tools: Optional list of tool definitions
            temperature: Model temperature
            max_tokens: Maximum tokens to generate

        Returns:
            The formatted request body
        """
        pass

    @abstractmethod
    def parse_response(self, response: Dict[str, Any]) -> str:
        """Parse a response from the model.

        Args:
            response: Raw response from the model

        Returns:
            The extracted response text
        """
        pass

    @abstractmethod
    def parse_stream_chunk(self, chunk: Dict[str, Any]) -> Optional[str]:
        """Parse a chunk from a streaming response.

        Args:
            chunk: A chunk from the streaming response

        Returns:
            The extracted text from this chunk, if any
        """
        pass

    def parse_tool_calls(self, chunk: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse tool calls from a response chunk.

        Looks for tool calls in the format:
        {"tool_calls": [{"name": "tool_name", "parameters": {...}}]}

        Args:
            chunk: Response chunk that may contain tool calls

        Returns:
            List of parsed tool calls
        """
        tool_calls = []
        if text := self.parse_stream_chunk(chunk):
            try:
                # Try to parse any JSON objects in the text
                import re

                json_matches = re.finditer(r"\{(?:[^{}]|(?R))*\}", text)
                for match in json_matches:
                    try:
                        json_obj = json.loads(match.group())
                        if "tool_calls" in json_obj:
                            tool_calls.extend(json_obj["tool_calls"])
                    except json.JSONDecodeError:
                        continue
            except Exception:
                pass
        return tool_calls

    def format_tool_description(self, tools: List[Dict[str, Any]]) -> str:
        """Format tools into a description that can be understood by the model.

        Args:
            tools: List of tool schemas

        Returns:
            A natural language description of the available tools
        """
        if not tools:
            return ""

        descriptions = ["You have access to the following tools:"]
        for tool in tools:
            desc = [
                f"\n{tool['name']}: {tool['description']}",
                "Parameters:",
            ]

            params = tool["parameters"].get("properties", {})
            required = tool["parameters"].get("required", [])

            for param_name, param_info in params.items():
                req = "(required)" if param_name in required else "(optional)"
                desc.append(
                    f"- {param_name}: {param_info.get('description', '')} {req}"
                )

            descriptions.extend(desc)

        descriptions.append(
            "\nTo use a tool, you MUST use this exact JSON format in your response:"
        )
        descriptions.append(
            '{"tool_calls": [{"name": "tool_name", "parameters": {"param1": "value1", ...}}]}'
        )
        descriptions.append("\nFor example:")
        descriptions.append(
            '{"tool_calls": [{"name": "current_time", "parameters": {"format": "%Y-%m-%d %H:%M:%S", "timezone": "UTC"}}]}'
        )
        descriptions.append(
            "\nAfter using a tool, continue your response based on the tool's result."
        )

        return "\n".join(descriptions)
