"""Agency implementation for orchestrating multi-agent communication."""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4

from ..agents.base import BedrockAgent
from ..events import EventSystem  # Import here to avoid circular imports
from ..memory.base import Message, SimpleMemory
from ..tools.base import BaseTool
from ..tools.send_message import SendMessageTool
from ..types import AgentResponse, ToolCall
from .thread import Run, Thread


class Agency:
    """An agency manages communication between multiple agents.

    The Agency:
    1. Maintains the communication graph between agents
    2. Routes messages to appropriate agents via threads
    3. Manages shared memory and state

    The Agency automatically creates a coordinator agent that:
    - Acts as the main interface with users
    - Routes requests to appropriate specialist agents
    - Manages complex tasks requiring multiple agents
    """

    def __init__(
        self,
        specialists: List[BedrockAgent],
        shared_instructions: Optional[str] = None,
        shared_memory: Optional[SimpleMemory] = None,
        model_id: str = "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    ) -> None:
        """Initialize the agency.

        Args:
            specialists: List of specialist agents that will handle specific tasks
            shared_instructions: Optional instructions shared by all agents
            shared_memory: Optional shared memory system
            model_id: Model ID to use for coordinator agent (defaults to Claude)
        """
        self.shared_memory = shared_memory or SimpleMemory()
        self.shared_instructions = shared_instructions
        self.threads: Dict[str, Thread] = {}
        self.event_system = EventSystem()

        # Initialize agent storage
        self.agents: Dict[str, BedrockAgent] = {}
        self.communication_paths: Dict[str, List[str]] = {}

        # Create coordinator agent
        self.coordinator = self._create_coordinator(model_id, specialists)

        # Add specialists and set up communication paths
        self._setup_specialists(specialists)

        # Add SendMessage tool to all agents
        self._setup_agent_communication()

        # Create main thread with coordinator agent
        self.main_thread = self._create_main_thread()

    def _create_coordinator(
        self, model_id: str, specialists: List[BedrockAgent]
    ) -> BedrockAgent:
        """Create the coordinator agent.

        Args:
            model_id: Model ID to use for coordinator
            specialists: List of specialists to coordinate

        Returns:
            The created coordinator agent
        """
        # Build coordinator's system prompt
        specialist_descriptions = []
        for agent in specialists:
            desc = (
                f"- {agent.name}: {agent.system_prompt}"
                if agent.system_prompt
                else f"- {agent.name}"
            )
            tools = [f"  * {t.name}: {t.description}" for t in agent.tools.values()]
            if tools:
                desc += "\n  Tools:\n" + "\n".join(tools)
            specialist_descriptions.append(desc)

        system_prompt = f"""You are the coordinator agent responsible for managing communication and task routing in this agency.

Available specialists:
{chr(10).join(specialist_descriptions)}

Your responsibilities:
1. Act as the main interface with users
2. Route requests to appropriate specialists using the SendMessage tool:
   - For calculations, send to the calculator specialist
   - For time-related queries, send to the time_expert specialist
3. For complex tasks that require multiple specialists:
   - Break down the task into subtasks
   - Route each subtask to the appropriate specialist
   - Combine their responses into a coherent answer

IMPORTANT: Always delegate tasks to specialists rather than trying to handle them yourself. Use the SendMessage tool to communicate with specialists."""

        # Create coordinator agent with only SendMessage tool
        coordinator = BedrockAgent(
            name="coordinator", model_id=model_id, system_prompt=system_prompt
        )

        # Add to agents dict
        self.agents[coordinator.name] = coordinator
        self.communication_paths[coordinator.name] = [
            "user"
        ]  # Coordinator can talk to user

        return coordinator

    def _setup_specialists(self, specialists: List[BedrockAgent]) -> None:
        """Set up specialist agents and their communication paths.

        Args:
            specialists: List of specialist agents to set up
        """
        for specialist in specialists:
            # Add specialist to agents dict
            self.agents[specialist.name] = specialist

            # Set up communication paths
            if specialist.name not in self.communication_paths:
                self.communication_paths[specialist.name] = []

            # Coordinator can talk to all specialists
            self.communication_paths[self.coordinator.name].append(specialist.name)

    def _create_main_thread(self) -> Thread:
        """Create the main thread with the coordinator agent.

        Returns:
            The created main thread
        """
        thread = Thread(self.coordinator)
        thread.event_system = self.event_system  # Connect event system
        self.threads[thread.id] = thread
        return thread

    def get_completion(
        self,
        message: str,
        recipient_agent: Optional[BedrockAgent] = None,
        additional_instructions: Optional[str] = None,
        thread_id: Optional[str] = None,
    ) -> str:
        """Get a completion from an agent.

        Args:
            message: Message to process
            recipient_agent: Optional specific agent to send message to
            additional_instructions: Optional additional instructions
            thread_id: Optional thread ID to use (creates new if not provided)

        Returns:
            Response from the agent
        """
        # Get or create thread
        thread = None
        if thread_id:
            thread = self.get_thread(thread_id)
            if not thread:
                raise ValueError(f"Thread {thread_id} not found")
        else:
            # Use main thread if no specific thread requested
            thread = self.main_thread

        # Switch agent if requested
        if recipient_agent:
            thread.agent = recipient_agent

        if not thread.agent:
            raise ValueError(f"Thread {thread.id} has no agent assigned")

        # Create run start event
        run_start_id = self.event_system.create_event(
            type="run_start",
            agent_name=thread.agent.name,
            run_id=thread.current_run.id if thread.current_run else "none",
            thread_id=thread.id,
            details={"message": message},
        )
        self.event_system.start_event_scope(run_start_id)

        try:
            # Add message to memory with metadata
            self.shared_memory.add_message(
                Message(
                    role="user",
                    content=message,
                    timestamp=datetime.now(),
                    thread_id=thread.id,
                    metadata={
                        "timestamp": datetime.now().isoformat(),
                        "thread_id": thread.id,
                        "run_id": thread.current_run.id if thread.current_run else None,
                        "event_id": run_start_id,
                    },
                )
            )

            # Process message and get response
            response = thread.process_message(message)

            # Add response to memory with metadata
            self.shared_memory.add_message(
                Message(
                    role="assistant",
                    content=response,
                    timestamp=datetime.now(),
                    thread_id=thread.id,
                    metadata={
                        "timestamp": datetime.now().isoformat(),
                        "thread_id": thread.id,
                        "run_id": thread.current_run.id if thread.current_run else None,
                        "agent_name": thread.agent.name,
                        "event_id": run_start_id,
                    },
                )
            )

            # Create run complete event
            self.event_system.create_event(
                type="run_complete",
                agent_name=thread.agent.name,
                run_id=thread.current_run.id if thread.current_run else "none",
                thread_id=thread.id,
                details={"response": response},
            )

            return response

        finally:
            self.event_system.end_event_scope()

    def create_thread(self, agent_name: Optional[str] = None) -> Thread:
        """Create a new thread.

        Args:
            agent_name: Optional name of agent to assign to thread

        Returns:
            The created thread
        """
        if agent_name and agent_name not in self.agents:
            raise ValueError(f"Agent {agent_name} not found")

        agent = self.agents[agent_name] if agent_name else None
        thread = Thread(agent) if agent else None
        thread.event_system = self.event_system  # Connect event system
        self.threads[thread.id] = thread
        return thread

    def get_thread(self, thread_id: str) -> Optional[Thread]:
        """Get a thread by ID.

        Args:
            thread_id: ID of thread to retrieve

        Returns:
            The thread if found, None otherwise
        """
        return self.threads.get(thread_id)

    def get_run(self, thread_id: str, run_id: str) -> Optional[Run]:
        """Get a specific run from a thread.

        Args:
            thread_id: ID of thread containing the run
            run_id: ID of run to retrieve

        Returns:
            The run if found, None otherwise
        """
        thread = self.get_thread(thread_id)
        if thread:
            return thread.get_run(run_id)
        return None

    def cancel_run(self, thread_id: str, run_id: str) -> bool:
        """Cancel a specific run in a thread.

        Args:
            thread_id: ID of thread containing the run
            run_id: ID of run to cancel

        Returns:
            True if run was cancelled, False otherwise
        """
        thread = self.get_thread(thread_id)
        if thread:
            return thread.cancel_run(run_id)
        return False

    def _setup_agent_communication(self) -> None:
        """Set up communication tools for all agents."""
        for agent_name, agent in self.agents.items():
            # Get valid recipients for this agent
            valid_recipients = self.communication_paths.get(agent_name, [])
            if not valid_recipients:
                continue

            # Create SendMessage tool with valid recipients
            send_tool = SendMessageTool(
                valid_recipients=valid_recipients,
                description=f"Send a message to another agent. Valid recipients: {', '.join(valid_recipients)}",
                agency=self,  # Pass agency instance to tool
            )

            # Add tool to agent
            agent.tools[send_tool.name] = send_tool

    def _parse_agency_chart(
        self, chart: List[Union[BedrockAgent, List[BedrockAgent]]]
    ) -> None:
        """Parse the agency chart to build communication paths."""
        for item in chart:
            if isinstance(item, BedrockAgent):
                # Single agent - can talk to user
                self.agents[item.name] = item
                self.communication_paths[item.name] = ["user"]
            elif isinstance(item, list) and len(item) == 2:
                # Agent pair - first can talk to second
                agent1, agent2 = item
                self.agents[agent1.name] = agent1
                self.agents[agent2.name] = agent2

                # Initialize paths if needed
                if agent1.name not in self.communication_paths:
                    self.communication_paths[agent1.name] = []
                if agent2.name not in self.communication_paths:
                    self.communication_paths[agent2.name] = []

                # Add communication path
                self.communication_paths[agent1.name].append(agent2.name)

    def add_agent(
        self, agent: BedrockAgent, can_talk_to: Optional[List[str]] = None
    ) -> None:
        """Add a new agent to the agency."""
        self.agents[agent.name] = agent
        self.communication_paths[agent.name] = can_talk_to or []

        # Update SendMessage tool for this agent
        if can_talk_to:
            send_tool = SendMessageTool(
                valid_recipients=can_talk_to,
                description=f"Send a message to another agent. Valid recipients: {', '.join(can_talk_to)}",
            )
            agent.tools[send_tool.name] = send_tool

    def get_agent(self, name: str) -> Optional[BedrockAgent]:
        """Get an agent by name."""
        return self.agents.get(name)

    def get_memory(self) -> SimpleMemory:
        """Get the shared memory system."""
        return self.shared_memory

    def get_event_trace(self, run_id: Optional[str] = None) -> str:
        """Get a formatted trace of events.

        Args:
            run_id: Optional run ID to filter events by

        Returns:
            Formatted string of events in chronological order
        """
        events = self.event_system.get_events(run_id=run_id)
        return "\n\n".join(self.event_system.format_event(event) for event in events)
