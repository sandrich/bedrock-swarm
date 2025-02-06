"""Claude model implementation."""

import json
from typing import Any, Dict, List, Optional, cast

from botocore.client import BaseClient
from botocore.exceptions import ClientError

from ..exceptions import ModelInvokeError, ResponseParsingError, ToolExecutionError
from ..tools.base import BaseTool
from .base import BedrockModel


class Claude35Model(BedrockModel):
    """Implementation for Claude 3.5 models."""

    def __init__(self) -> None:
        """Initialize the model."""
        super().__init__()

    def get_default_max_tokens(self) -> int:
        """Get the default maximum tokens for this model."""
        return 4096

    def supports_tools(self) -> bool:
        """Check if this model supports tools/function calling."""
        return True

    def supports_streaming(self) -> bool:
        """Check if this model supports streaming responses."""
        return True

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
        # Format request
        request = self.format_request(
            message=message,
            system=system,
            tools=tools,
            temperature=temperature,
            max_tokens=max_tokens or self.get_default_max_tokens(),
        )

        try:
            # Invoke model with streaming
            response = client.invoke_model_with_response_stream(
                modelId="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
                body=json.dumps(request),
            )

            # Process streaming response
            response_text = ""
            for event in response.get("body"):
                try:
                    chunk = json.loads(event.get("chunk").get("bytes").decode())
                except json.JSONDecodeError as e:
                    raise ResponseParsingError(f"Error parsing chunk: {str(e)}")

                # Handle error chunks
                if chunk.get("type") == "error":
                    raise ModelInvokeError(
                        chunk.get("message", "Unknown streaming error")
                    )

                # Handle content chunks
                if text := self.parse_stream_chunk(chunk):
                    response_text += text
                    # Update token count from usage info
                    if "usage" in chunk:
                        self.last_token_count = chunk["usage"].get("output_tokens", 0)

                # Handle tool calls
                if tool_map and chunk.get("type") == "tool_calls":
                    for tool_call in chunk.get("tool_calls", []):
                        try:
                            tool = tool_map.get(tool_call["name"])
                            if not tool:
                                raise ToolExecutionError(
                                    f"Tool {tool_call['name']} not found"
                                )
                            result = tool.execute(**tool_call["parameters"])
                            response_text += (
                                f"\nTool {tool_call['name']} result: {result}\n"
                            )
                        except Exception as e:
                            raise ToolExecutionError(
                                f"Error executing tool {tool_call['name']}: {str(e)}"
                            )

            return response_text.strip()

        except ClientError as e:
            raise ModelInvokeError(f"Error invoking model: {str(e)}")
        except Exception as e:
            if isinstance(
                e, (ModelInvokeError, ResponseParsingError, ToolExecutionError)
            ):
                raise
            raise ModelInvokeError(f"Unexpected error: {str(e)}")

    def format_request(
        self,
        message: str,
        system: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> Dict[str, Any]:
        """Format a request for Bedrock's API."""
        # Format tool descriptions if any
        tool_desc = self.format_tool_description(tools) if tools else ""

        # Combine system instructions, tool descriptions, and message
        full_message = ""
        if system:
            full_message += f"{system}\n\n"
        if tool_desc:
            full_message += f"{tool_desc}\n\n"
        full_message += message

        request = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [
                {
                    "role": "user",
                    "content": full_message,
                }
            ],
        }

        return request

    def parse_response(self, response: Dict[str, Any]) -> str:
        """Parse a response from the model."""
        try:
            return cast(str, response.get("completion", "")).strip()
        except Exception as e:
            raise ResponseParsingError(f"Error parsing response: {str(e)}")

    def parse_stream_chunk(self, chunk: Dict[str, Any]) -> Optional[str]:
        """Parse a streaming chunk from Claude 3.5."""
        if chunk.get("type") == "content_block_delta":
            return cast(str, chunk.get("delta", {}).get("text", ""))
        return None

    # Removed parse_tool_calls since it's now in the base class
