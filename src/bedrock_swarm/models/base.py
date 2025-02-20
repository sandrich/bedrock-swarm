"""Base classes for Bedrock model implementations."""

import abc
import json
import logging
import time
from typing import Any, Dict, Optional

from botocore.client import BaseClient
from botocore.exceptions import ClientError

from ..exceptions import ModelInvokeError, ResponseParsingError
from ..types import AgentResponse

# Configure logger
logger = logging.getLogger(__name__)


class BedrockModel(abc.ABC):
    """Base class for Bedrock model implementations."""

    def __init__(self, model_id: str):
        """Initialize the model.

        Args:
            model_id: The Bedrock model ID to use
        """
        self._model_id = model_id
        self._config: Dict[str, Any] = {
            "max_tokens": 4096,  # Default maximum tokens
            "default_tokens": 2048,  # Default response length
        }

    def get_model_id(self) -> str:
        """Get the Bedrock model ID."""
        return self._model_id

    def set_config(self, config: Dict[str, Any]) -> None:
        """Set model-specific configuration.

        Args:
            config: Configuration dictionary with model settings
        """
        self._config.update(config)

    def validate_token_count(self, max_tokens: Optional[int] = None) -> int:
        """Validate and return the token count to use.

        Args:
            max_tokens: Requested maximum number of tokens. If not provided,
                       uses the model's default token count.

        Returns:
            The validated token count to use

        Raises:
            ValueError: If max_tokens exceeds the model's limit
        """
        # Use default token count if not specified
        token_count = max_tokens or self._config["default_tokens"]

        # Validate against model's maximum token limit
        if token_count > self._config["max_tokens"]:
            raise ValueError(
                f"max_tokens ({token_count}) exceeds model's limit "
                f"of {self._config['max_tokens']} tokens"
            )

        return token_count

    @abc.abstractmethod
    def format_request(
        self,
        message: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Format a request for the model.

        Args:
            message: The message to send to the model
            system: Optional system prompt
            temperature: Temperature for response generation (0.0 to 1.0)
            max_tokens: Maximum number of tokens to generate

        Returns:
            Formatted request dictionary
        """
        pass

    def process_response(self, response: Dict[str, Any]) -> AgentResponse:
        """Process a response from this specific model.

        Args:
            response: Raw response from the model

        Returns:
            Processed response as either a message or tool call

        Raises:
            ResponseParsingError: If response cannot be parsed
        """
        try:
            # Extract content from response (implementation specific)
            try:
                content = self._extract_content(response)
            except ResponseParsingError:
                # Return empty message for invalid responses
                return {"type": "message", "content": ""}

            # Try to parse as JSON if it looks like JSON
            if content.startswith("{") and content.endswith("}"):
                try:
                    parsed = json.loads(content)

                    # Validate response format
                    if parsed.get("type") == "tool_call" and parsed.get("tool_calls"):
                        return parsed
                    elif parsed.get("type") == "message":
                        return {"type": "message", "content": parsed.get("content", "")}
                except json.JSONDecodeError:
                    pass

            # If not valid JSON or not proper format, return as message
            return {"type": "message", "content": content}

        except Exception as e:
            raise ResponseParsingError(f"Error processing response: {str(e)}")

    @abc.abstractmethod
    def _extract_content(self, response: Dict[str, Any]) -> str:
        """Extract the content from a model response.

        Args:
            response: Raw response from the model

        Returns:
            Extracted content as string

        Raises:
            ResponseParsingError: If content cannot be extracted
        """
        pass

    def _invoke_with_retry(
        self,
        client: BaseClient,
        request: Dict[str, Any],
        max_retries: int = 5,
        initial_delay: float = 1.0,
    ) -> Dict[str, Any]:
        """Invoke model with exponential backoff retry.

        Args:
            client: Bedrock client
            request: Request body
            max_retries: Maximum number of retries
            initial_delay: Initial delay in seconds

        Returns:
            Model response

        Raises:
            ModelInvokeError: If all retries fail
        """
        delay = initial_delay
        last_error = None

        for attempt in range(max_retries):
            try:
                response = client.invoke_model_with_response_stream(
                    modelId=self.get_model_id(),
                    body=json.dumps(request),
                )
                return response

            except ClientError as e:
                last_error = e
                if (
                    e.response["Error"]["Code"] == "ThrottlingException"
                    and attempt < max_retries - 1
                ):
                    logger.debug(
                        f"Rate limited. Waiting {delay:.1f}s before retry {attempt + 1}/{max_retries}"
                    )
                    time.sleep(delay)
                    delay *= 2  # Exponential backoff
                    continue
                raise ModelInvokeError(f"Error invoking model: {str(e)}")

        raise ModelInvokeError(f"Max retries exceeded: {str(last_error)}")

    def invoke(
        self,
        client: BaseClient,
        message: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> AgentResponse:
        """Invoke the model with a message.

        This defines the high-level flow:
        1. Format request (model-specific)
        2. Call Bedrock with retry
        3. Process response (model-specific)
        """
        try:
            # Format request (model-specific)
            request = self.format_request(
                message=message,
                system=system,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            # Call Bedrock with retry
            response = self._invoke_with_retry(client, request)

            # Process response
            return self.process_response(response)

        except Exception as e:
            raise ModelInvokeError(f"Error invoking model: {str(e)}")
