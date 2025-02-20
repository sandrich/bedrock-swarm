"""Tool for sending messages between agents."""

import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from ..tools.base import BaseTool

if TYPE_CHECKING:
    from ..agency.agency import Agency

logger = logging.getLogger(__name__)


class SendMessageTool(BaseTool):
    """Tool for sending messages between agents."""

    def __init__(
        self,
        valid_recipients: Optional[List[str]] = None,
        description: Optional[str] = None,
        agency: Optional["Agency"] = None,
    ) -> None:
        """Initialize the send message tool.

        Args:
            valid_recipients: Optional list of valid recipient names
            description: Optional tool description
            agency: Optional reference to the agency
        """
        self._name = "SendMessage"
        self._description = description or "Send a message to another agent"
        self._valid_recipients = valid_recipients or []
        self._agency = agency

    @property
    def name(self) -> str:
        """Get tool name."""
        return self._name

    @property
    def description(self) -> str:
        """Get tool description."""
        return self._description

    def get_schema(self) -> Dict[str, Any]:
        """Get JSON schema for the send message tool."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "recipient": {
                        "type": "string",
                        "description": f"Name of the recipient agent. Valid recipients: {', '.join(self._valid_recipients)}",
                    },
                    "message": {
                        "type": "string",
                        "description": "Message to send to the recipient",
                    },
                },
                "required": ["recipient", "message"],
            },
        }

    def _execute_impl(self, *, recipient: str, message: str, **kwargs: Any) -> str:
        """Execute the send message tool.

        Args:
            recipient: Name of the recipient agent
            message: Message to send
            **kwargs: Additional keyword arguments

        Returns:
            Response from the recipient agent

        Raises:
            ValueError: If recipient is not valid
        """
        if recipient not in self._valid_recipients:
            raise ValueError(f"Invalid recipient: {recipient}")

        # Get thread from kwargs
        thread = kwargs.get("thread")
        if not thread:
            raise ValueError("No thread provided")

        # Process message through recipient's thread
        recipient_agent = self._agency.get_agent(recipient)
        if not recipient_agent:
            raise ValueError(f"Recipient agent {recipient} not found")

        return self._agency.get_completion(
            message=message,
            recipient_agent=recipient_agent,
            thread_id=thread.id,
        )
