"""Tool for sending messages between agents."""

from typing import Any, Dict, List, Optional

from ..agency.thread import Thread
from ..tools.base import BaseTool


class SendMessageTool(BaseTool):
    """Tool for sending messages between agents."""

    def __init__(
        self,
        name: str = "SendMessage",
        description: str = "Send a message to another agent",
        valid_recipients: Optional[List[str]] = None,
        agency=None,  # Will be set by Agency when adding tool
    ) -> None:
        """Initialize the send message tool.

        Args:
            name: Name of the tool
            description: Description of the tool
            valid_recipients: Optional list of valid recipient names
            agency: Agency instance (will be set by Agency)
        """
        self._name = name
        self._description = description
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
        """Get JSON schema for the tool."""
        recipients_desc = (
            f"Valid recipients are: {', '.join(self._valid_recipients)}"
            if self._valid_recipients
            else "Recipient agent to send the message to"
        )

        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "recipient": {
                        "type": "string",
                        "description": recipients_desc,
                    },
                    "message": {
                        "type": "string",
                        "description": "Message to send to the recipient agent",
                    },
                },
                "required": ["recipient", "message"],
            },
        }

    def _execute_impl(
        self,
        *,
        recipient: str,
        message: str,
        **kwargs: Any,
    ) -> str:
        """Execute the send message tool.

        Args:
            recipient: Name of recipient agent
            message: Message to send
            **kwargs: Additional keyword arguments (unused)

        Returns:
            Response from the recipient agent

        Raises:
            ValueError: If recipient is invalid or agency not set
        """
        if not self._agency:
            raise ValueError(
                "SendMessageTool not properly initialized - agency not set"
            )

        if self._valid_recipients and recipient not in self._valid_recipients:
            raise ValueError(
                f"Invalid recipient. Valid recipients are: {', '.join(self._valid_recipients)}"
            )

        # Get the recipient agent
        recipient_agent = self._agency.get_agent(recipient)
        if not recipient_agent:
            raise ValueError(f"Recipient agent {recipient} not found")

        # Create a new thread for the recipient
        thread = self._agency.create_thread(recipient)

        # Get response from recipient
        response = self._agency.get_completion(message=message, thread_id=thread.id)

        return response
