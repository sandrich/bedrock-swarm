"""Agency implementation for orchestrating multi-agent communication."""


import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from ..agents.base import BedrockAgent
from ..events import EventSystem
from ..memory.base import Message, SimpleMemory
from ..tools.planning import PlanningTool
from ..tools.send_message import SendMessageTool
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

        # Add tools to all agents
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
            # Get agent's tools and their descriptions
            tools = [f"    - {t.name}: {t.description}" for t in agent.tools.values()]

            # Build capability description
            desc = [
                f"- {agent.name}:",
                "  Expertise:",
                f"    {agent.system_prompt}",
                "  Available Tools:",
            ]
            if tools:
                desc.extend(tools)
            specialist_descriptions.append("\n".join(desc))

        system_prompt = f"""You are an expert task planner specializing in creating structured, actionable plans using specialized tools.

AVAILABLE SPECIALISTS AND THEIR CAPABILITIES:
{chr(10).join(specialist_descriptions)}

Your job is to create structured plans using the create_plan tool with this EXACT JSON structure:
{{
  "steps": [
    {{
      "step_number": 1,
      "description": "[Concise, clear action instruction]",
      "specialist": "[specialist name]",
      "requires_results_from": [optional step numbers]
    }}
  ],
  "final_output_format": "[Specify exact output expectations]"
}}

STRICT FORMATTING RULES:
- "steps" must be an array of objects
- Each step requires:
  * Incrementing step_number
  * Clear description
  * Valid specialist name
  * Optional dependency tracking

VALIDATION RULES:
- Each specialist must only perform operations within their constraints
- Steps requiring calculation must use calculator
- Time-related operations must use time_expert
- No specialist can perform operations outside their constraints
- Time calculations must be split:
  * calculator does the math
  * time_expert handles time queries and conversions
- Dependencies must be explicit when using results from other steps
- Each step must contain exactly one operation
- No combining multiple operations in one step

EXAMPLE - CORRECT:
{{
  "steps": [
    {{
      "step_number": 1,
      "description": "Calculate 15 * 7",
      "specialist": "calculator"
    }},
    {{
      "step_number": 2,
      "description": "Calculate the time {{MINUTES}} minutes from now",
      "specialist": "time_expert",
      "requires_results_from": [1]
    }}
  ],
  "final_output_format": "In {{MINUTES}} minutes, the time will be {{TIME}}"
}}

EXAMPLE - WRONG (DO NOT DO THIS):
{{
  "steps": [
    "1. Calculate 2 + 2",
    "2. Calculate future time"
  ]
}}

IMPORTANT: Respond ONLY with the JSON plan, no other text."""

        # Create coordinator agent with planning tool
        coordinator = BedrockAgent(
            name="coordinator",
            model_id=model_id,
            system_prompt=system_prompt,
            tools=[PlanningTool()],
        )

        # Set agency reference
        coordinator._agency = self

        # Add to agents dict
        self.agents[coordinator.name] = coordinator
        self.communication_paths[coordinator.name] = ["user"]

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

    def process_request(self, request: str) -> str:
        """Process a user request through planning, execution, and response phases.

        Args:
            request: The user's request

        Returns:
            The final response after plan execution
        """
        # Phase 1: Planning
        # Have coordinator create a plan using the planning tool
        planning_message = f"Please create a plan to handle this request: {request}"
        self.get_completion(
            message=planning_message,
            recipient_agent=self.coordinator,
            thread_id=self.main_thread.id,
        )

        # The coordinator should have used create_plan tool which validates the plan
        # and stores it in self.current_plan
        if not hasattr(self, "current_plan"):
            raise ValueError(
                "Coordinator failed to create a valid plan using create_plan tool"
            )

        # Phase 2: Execution
        # Execute each step and collect results
        self.event_system.create_event(
            type="execution_start",
            agent_name="agency",
            run_id=self.main_thread.current_run.id
            if self.main_thread.current_run
            else "none",
            thread_id=self.main_thread.id,
            details={"plan": self.current_plan},
        )

        results = self.execute_plan(self.current_plan)

        self.event_system.create_event(
            type="execution_complete",
            agent_name="agency",
            run_id=self.main_thread.current_run.id
            if self.main_thread.current_run
            else "none",
            thread_id=self.main_thread.id,
            details={"results": results},
        )

        # Phase 3: Response Formatting
        # Have coordinator create a natural response from the results
        formatting_message = f"""Please create a natural, clear response using these results.

Format Guide: {self.current_plan['final_output_format']}

Results from execution:
{chr(10).join(f'Step {k}: {v}' for k, v in results.items())}

Remember to:
1. Use natural, clear language
2. Include all relevant information
3. Follow the format guide
4. Make it easy for the user to understand"""

        final_response = self.get_completion(
            message=formatting_message,
            recipient_agent=self.coordinator,
            thread_id=self.main_thread.id,
        )

        self.event_system.create_event(
            type="response_complete",
            agent_name="agency",
            run_id=self.main_thread.current_run.id
            if self.main_thread.current_run
            else "none",
            thread_id=self.main_thread.id,
            details={"response": final_response},
        )

        return final_response

    def execute_plan(self, plan: Dict[str, Any]) -> Dict[str, str]:
        """Execute a plan by gathering information from specialists.

        Args:
            plan: The validated plan to execute

        Returns:
            Dictionary mapping step numbers to results
        """
        results = {}

        # Execute each step in sequence
        for step in plan["steps"]:
            step_num = str(step["step_number"])

            # Check dependencies are met
            if "requires_results_from" in step:
                for dep in step["requires_results_from"]:
                    if str(dep) not in results:
                        raise ValueError(f"Missing required result from step {dep}")

            # Get the specialist
            specialist = self.agents.get(step["specialist"])
            if not specialist:
                raise ValueError(f"Specialist {step['specialist']} not found")

            # Prepare context from dependencies
            context = ""
            description = step["description"]

            if "requires_results_from" in step:
                context = "Previous results:\n"
                # Replace placeholders in description with actual values
                for dep in step["requires_results_from"]:
                    dep_str = str(dep)
                    context += f"Step {dep}: {results[dep_str]}\n"
                    # Extract the numeric result from previous step
                    if dep_str in results:
                        result_text = results[dep_str]
                        # Try to extract the first number from the result
                        if numbers := re.findall(r"\d+", result_text):
                            description = description.replace("{{MINUTES}}", numbers[0])
                            description = description.replace("{MINUTES}", numbers[0])

            # Execute the step
            message = f"{context}\nTask: {description}"
            result = self.get_completion(
                message=message,
                recipient_agent=specialist,
                thread_id=self.main_thread.id,
            )

            # Store the result
            results[step_num] = result

            # Create execution event
            self.event_system.create_event(
                type="step_complete",
                agent_name=specialist.name,
                run_id=self.main_thread.current_run.id
                if self.main_thread.current_run
                else "none",
                thread_id=self.main_thread.id,
                details={
                    "step_number": step_num,
                    "description": description,
                    "result": result,
                },
            )

        return results

    def format_response(self, results: Dict[str, str], format_guide: str) -> str:
        """Format the final response based on collected results.

        Args:
            results: Dictionary of step numbers to results
            format_guide: Guide for formatting the response

        Returns:
            Formatted final response
        """
        # Have coordinator format the response with all results
        compilation_message = f"""Please format the final response according to: {format_guide}

Results from each step:
{chr(10).join(f'Step {k}: {v}' for k, v in results.items())}"""

        return self.get_completion(
            message=compilation_message,
            recipient_agent=self.coordinator,
            thread_id=self.main_thread.id,
        )
