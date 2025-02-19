"""Titan model implementation."""

import json
import logging
from typing import Any, Dict, Optional

from ..exceptions import ResponseParsingError
from .base import BedrockModel

# Configure logger
logger = logging.getLogger(__name__)


class TitanModel(BedrockModel):
    """Implementation for Amazon Titan models."""

    def format_request(
        self,
        message: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Format a request for Titan.

        Args:
            message: The message to send to the model
            system: Optional system prompt
            temperature: Temperature for response generation (0.0 to 1.0)
            max_tokens: Maximum number of tokens to generate

        Returns:
            Formatted request dictionary

        Raises:
            ValueError: If max_tokens exceeds the model's limit
        """
        # Combine system prompt and message if provided
        prompt = f"{system}\n\n{message}" if system else message

        # Validate token count
        token_count = self.validate_token_count(max_tokens)

        request = {
            "inputText": prompt,
            "textGenerationConfig": {
                "temperature": temperature,
                "topP": 1,
                "maxTokenCount": token_count,
                "stopSequences": [],
            },
        }
        return request

    def _extract_content(self, response: Dict[str, Any]) -> str:
        """Extract content from Titan response.

        Args:
            response: Raw response from Titan

        Returns:
            Extracted content as string

        Raises:
            ResponseParsingError: If content cannot be extracted
        """
        content = []
        logger.debug("Processing response: %s", response)

        for event in response["body"]:
            try:
                chunk = json.loads(event.get("chunk").get("bytes").decode())
                logger.debug("Processing chunk: %s", chunk)
                if "outputText" in chunk:
                    content.append(chunk["outputText"])
            except json.JSONDecodeError as e:
                raise ResponseParsingError(f"Error parsing chunk: {str(e)}")
            except (KeyError, AttributeError) as e:
                raise ResponseParsingError(f"Invalid chunk format: {str(e)}")

        # Join and clean up the content
        return "".join(content).strip()
