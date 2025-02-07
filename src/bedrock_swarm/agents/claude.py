"""Claude agent implementation."""

from typing import Any, Dict

from .base import BedrockAgent


class ClaudeAgent(BedrockAgent):
    """Claude-specific agent implementation."""

    def _get_model_response(self, prompt: str) -> Dict[str, Any]:
        """Get response from Claude model.

        Args:
            prompt: Formatted prompt string

        Returns:
            Dict with response and any metadata
        """
        # Get bedrock client
        client = self.session.client(
            "bedrock-runtime",
            endpoint_url=self.aws_config.endpoint_url,
        )

        # Format tools if available
        tools = None
        if self.tools and self.model.supports_tools():
            tools = [tool.get_schema() for tool in self.tools.values()]

        # Get response from model
        response = self.model.process_message(
            client=client,
            message=prompt,
            system=self.system_prompt or "",
            tools=tools,
            temperature=0.7,  # Default temperature
        )

        return response
