"""Module for managing swarms of agents working together."""

from typing import Any, Dict, List, Optional

from ..agents.base import BedrockAgent


class Swarm:
    """A swarm of agents working together."""

    def __init__(self, agents: Dict[str, BedrockAgent]):
        """Initialize the swarm.

        Args:
            agents (Dict[str, BedrockAgent]): Map of agent ID to agent
        """
        self.agents = agents
        self.history: List[Dict[str, Dict[str, Any]]] = []

    def _format_context(self, prev_responses: List[str]) -> str:
        """Format the context string with previous responses.

        Args:
            prev_responses (List[str]): Previous responses from agents

        Returns:
            str: Formatted context string
        """
        context = (
            "Previous responses:\n"
            + "\n".join(f"- {r}" for r in prev_responses)
            + "\n\nWhat are your thoughts on the discussion so far?"
        )
        return context

    def _process_round(self, prev_responses: List[str]) -> Dict[str, Dict[str, Any]]:
        """Process a single round of discussion.

        Args:
            prev_responses (List[str]): Previous responses from agents

        Returns:
            Dict[str, Dict[str, Any]]: Map of agent ID to response
        """
        responses = {}
        for agent_id, agent in self.agents.items():
            context = self._format_context(prev_responses)
            response = agent.process_message(context)
            responses[agent_id] = {"content": response}
        return responses

    def discuss(self, topic: str, rounds: int = 3) -> List[Dict[str, Dict[str, Any]]]:
        """Have agents discuss a topic.

        Args:
            topic (str): Topic to discuss
            rounds (int): Number of rounds of discussion

        Returns:
            List[Dict[str, Dict[str, Any]]]: History of responses by round
        """
        # Initial round
        responses = {}
        for agent_id, agent in self.agents.items():
            response = agent.process_message(topic)
            responses[agent_id] = {"content": response}
        self.history.append(responses)

        # Subsequent rounds
        for _ in range(rounds - 1):
            prev_responses = [r["content"] for r in self.history[-1].values()]
            responses = self._process_round(prev_responses)
            self.history.append(responses)

        return self.history

    def add_agent(self, agent: BedrockAgent, agent_id: str) -> None:
        """Add an agent to the swarm.

        Args:
            agent (BedrockAgent): Agent to add
            agent_id (str): ID for the agent
        """
        if agent_id in self.agents:
            raise ValueError(f"Agent '{agent_id}' already exists")
        self.agents[agent_id] = agent

    def get_agent(self, agent_id: str) -> BedrockAgent:
        """Get an agent by ID.

        Args:
            agent_id (str): ID of the agent to get

        Returns:
            BedrockAgent: The agent if found

        Raises:
            KeyError: If agent is not found
        """
        if agent_id not in self.agents:
            raise KeyError(f"Agent '{agent_id}' not found")
        return self.agents[agent_id]

    def remove_agent(self, agent_id: str) -> bool:
        """Remove an agent from the swarm.

        Args:
            agent_id (str): ID of the agent to remove

        Returns:
            bool: True if agent was removed
        """
        if agent_id in self.agents:
            del self.agents[agent_id]
            return True
        return False

    def broadcast(
        self, message: str, exclude: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Broadcast a message to all agents.

        Args:
            message (str): Message to broadcast
            exclude (Optional[List[str]]): Agent IDs to exclude

        Returns:
            List[Dict[str, Any]]: List of agent responses
        """
        exclude = exclude or []
        responses = []

        for agent_id, agent in self.agents.items():
            if agent_id not in exclude:
                response = agent.process_message(message)
                responses.append({"agent_id": agent_id, "content": response})

        return responses

    def process_message(
        self,
        agent_id: str,
        message: str,
        tool_results: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """Process a message through a specific agent.

        Args:
            agent_id (str): ID of the agent to process the message
            message (str): Message to process
            tool_results (Optional[List[Dict[str, Any]]]): Optional results from tool executions

        Returns:
            str: Agent's response

        Raises:
            KeyError: If agent is not found
        """
        agent = self.get_agent(agent_id)
        return agent.process_message(message, tool_results=tool_results)
