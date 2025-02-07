"""Claude model implementation."""

import json
from typing import Any, Dict, Optional

from ..exceptions import ResponseParsingError
from .base import BedrockModel


class Claude35Model(BedrockModel):
    """Implementation for Claude 3.5 models."""

    def get_model_id(self) -> str:
        """Get the Bedrock model ID."""
        return "us.anthropic.claude-3-5-sonnet-20241022-v2:0"

    def format_request(
        self,
        message: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Format a request for Claude."""
        # Combine system prompt and message if provided
        content = f"{system}\n\n{message}" if system else message

        return {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens or 4096,
            "temperature": temperature,
            "messages": [{"role": "user", "content": content}],
        }

    def process_response(self, response: Dict[str, Any]) -> Dict[str, str]:
        """Process the response from the model.

        Args:
            response: Raw response from Bedrock

        Returns:
            Processed response with content and tool calls

        Raises:
            ResponseParsingError: If response cannot be parsed
        """
        content = []
        for event in response["body"]:
            try:
                chunk = json.loads(event.get("chunk").get("bytes").decode())
                if chunk.get("type") == "content_block_delta":
                    content.append(chunk["delta"]["text"])
            except json.JSONDecodeError as e:
                raise ResponseParsingError(f"Error parsing chunk: {str(e)}")
            except (KeyError, AttributeError) as e:
                raise ResponseParsingError(f"Invalid chunk format: {str(e)}")

        return {"content": "".join(content)}
