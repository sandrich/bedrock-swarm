"""Titan model implementation."""

import json
import logging
from typing import Any, Dict, Optional

from bedrock_swarm.exceptions import ModelInvokeError

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
            ValueError: If max_tokens exceeds the model's limit or temperature is invalid
        """
        # Validate temperature
        if not 0.0 <= temperature <= 1.0:
            raise ValueError("Temperature must be between 0.0 and 1.0")

        # Combine system prompt and message if provided
        prompt = f"{system}\n\n{message}" if system and system.strip() else message

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
                chunk = json.loads(event.get("chunk", {}).get("bytes", b"{}").decode())
                logger.debug("Processing chunk: %s", chunk)
                if "outputText" in chunk:
                    content.append(chunk["outputText"])
            except json.JSONDecodeError as e:
                raise ResponseParsingError(f"Error parsing chunk: {str(e)}")
            except (KeyError, AttributeError) as e:
                raise ResponseParsingError(f"Invalid chunk format: {str(e)}")

        # Join and clean up the content
        return " ".join(part.strip() for part in content).strip()

    def invoke(self, message: str, **kwargs: Any) -> Dict[str, Any]:
        """Invoke the model with a message.

        Args:
            message: The message to send to the model
            **kwargs: Additional arguments to pass to format_request

        Returns:
            Model response

        Raises:
            ModelInvokeError: If there is an error invoking the model
        """
        try:
            request = self.format_request(message, **kwargs)
            response = self.client.invoke_model_with_response_stream(
                modelId=self.get_model_id(),
                body=json.dumps(request).encode(),
            )
            return self.process_response(response)
        except Exception as e:
            raise ModelInvokeError(f"Error invoking model: {str(e)}")
