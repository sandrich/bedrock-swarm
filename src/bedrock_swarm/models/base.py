"""Base class for Bedrock model implementations."""

import json
import logging
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from botocore.client import BaseClient
from botocore.exceptions import ClientError

from ..exceptions import ModelInvokeError

# Configure logger
logger = logging.getLogger(__name__)


class BedrockModel(ABC):
    """Base class for Bedrock model implementations.

    This class defines the minimal interface for talking to Bedrock.
    Each model implementation handles its own request/response format.
    """

    @abstractmethod
    def get_model_id(self) -> str:
        """Get the Bedrock model ID."""
        pass

    @abstractmethod
    def format_request(
        self,
        message: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Format a request for this specific model."""
        pass

    @abstractmethod
    def process_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Process a response from this specific model."""
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
    ) -> Dict[str, Any]:
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

            # Process response (model-specific)
            return self.process_response(response)

        except Exception as e:
            raise ModelInvokeError(f"Error invoking model: {str(e)}")
