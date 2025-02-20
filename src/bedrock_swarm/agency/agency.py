"""Agency implementation for orchestrating multi-agent communication."""

import logging
from typing import Dict, Optional

from ..agents.base import BedrockAgent
from ..events import EventSystem
from ..memory.base import SimpleMemory
from ..tools.send_message import SendMessageTool
from .thread import Thread

logger = logging.getLogger(__name__)


class Agency:
    """An agency manages communication between multiple agents.

    The Agency:
    1. Maintains a static mapping of agents to their roles/capabilities
    2. Routes messages to appropriate agents based on their defined roles
    3. Manages shared memory between agents
    """

    def __init__(
        self,
        agents: Dict[str, BedrockAgent],
        shared_memory: Optional[SimpleMemory] = None,
    ) -> None:
        """Initialize the agency.

        Args:
            agents: Dictionary mapping agent names to their BedrockAgent instances
            shared_memory: Optional shared memory system
        """
        self.agents = agents
        self.shared_memory = shared_memory or SimpleMemory()
        self.threads: Dict[str, Thread] = {}
        self.event_system = EventSystem()

        # Set up inter-agent communication
        self._setup_agent_communication()

    def _setup_agent_communication(self) -> None:
        """Set up communication tools between agents."""
        for agent_name, agent in self.agents.items():
            # Create list of valid recipients (all agents except self)
            valid_recipients = [
                name for name in self.agents.keys() if name != agent_name
            ]

            # Add SendMessageTool to each agent
            send_tool = SendMessageTool(agency=self, valid_recipients=valid_recipients)
            agent.tools["send_message"] = send_tool

    def get_agent(self, agent_name: str) -> BedrockAgent:
        """Get an agent by name.

        Args:
            agent_name: Name of the agent to retrieve

        Returns:
            The requested BedrockAgent instance

        Raises:
            KeyError: If agent is not found
        """
        if agent_name not in self.agents:
            raise KeyError(f"Agent '{agent_name}' not found")
        return self.agents[agent_name]

    def get_completion(
        self,
        message: str,
        recipient_agent: BedrockAgent,
        thread_id: str,
    ) -> str:
        """Get a completion from a specific agent.

        Args:
            message: Message to process
            recipient_agent: Agent to process the message
            thread_id: ID of the thread making the request

        Returns:
            Response from the agent
        """
        # Create new thread for recipient if needed
        recipient_thread_id = f"{recipient_agent.name}_{thread_id}"
        if recipient_thread_id not in self.threads:
            thread = Thread(recipient_agent)
            thread.event_system = self.event_system
            self.threads[recipient_thread_id] = thread

        # Process message through recipient's thread
        thread = self.threads[recipient_thread_id]
        return thread.process_message(message)

    def process_request(self, message: str, agent_name: str) -> str:
        """Process a request through a specific agent.

        Args:
            message: Message to process
            agent_name: Name of the agent to handle the request

        Returns:
            Response from the agent

        Raises:
            KeyError: If agent is not found
        """
        # Get or create thread for this agent
        thread_id = f"{agent_name}_thread"
        if thread_id not in self.threads:
            agent = self.get_agent(agent_name)
            thread = Thread(agent)
            thread.event_system = self.event_system
            self.threads[thread_id] = thread

        # Process message through thread
        thread = self.threads[thread_id]
        return thread.process_message(message)

    def add_agent(self, agent: BedrockAgent) -> None:
        """Add a new agent to the agency.

        Args:
            agent: Agent to add
        """
        self.agents[agent.name] = agent
        # Update communication tools after adding new agent
        self._setup_agent_communication()

    def get_memory(self) -> SimpleMemory:
        """Get the shared memory system."""
        return self.shared_memory
