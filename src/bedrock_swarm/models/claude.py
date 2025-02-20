"""Claude model implementation."""

import json
from typing import Any, Dict, Optional

from ..exceptions import ResponseParsingError
from .base import BedrockModel


class ClaudeModel(BedrockModel):
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
        """Format a request for Claude.

        Args:
            message: The message to send to the model
            system: Optional system prompt
            temperature: Temperature for response generation (0.0 to 1.0)
            max_tokens: Maximum number of tokens to generate

        Returns:
            Formatted request dictionary
        """
        # Combine system prompt and message if provided
        content = f"{system}\n\n{message}" if system else message

        return {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens or 4096,
            "temperature": temperature,
            "messages": [{"role": "user", "content": content}],
        }

    def _extract_content(self, response: Dict[str, Any]) -> str:
        """Extract content from Claude response.

        Args:
            response: Raw response from Claude

        Returns:
            Extracted content as string

        Raises:
            ResponseParsingError: If content cannot be extracted
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

        return "".join(content)
