"""Core Agency implementation for orchestrating multi-agent systems."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from uuid import uuid4

from ..agents.base import BedrockAgent
from ..tools.base import BaseTool
from ..types import ToolCallResult
from .thread import Thread, ThreadMessage


@dataclass
class WorkflowStep:
    """A step in a workflow."""

    id: str = field(default_factory=lambda: str(uuid4()))
    agent: str = ""
    instructions: str = ""
    tools: List[BaseTool] = field(default_factory=list)
    input_from: List[str] = field(default_factory=list)
    use_initial_input: bool = True
    requires: List[str] = field(default_factory=list)


@dataclass
class Workflow:
    """A workflow of steps to be executed."""

    name: str
    steps: List[WorkflowStep]


class Agency:
    """An agency manages multiple threads of conversation with agents."""

    def __init__(
        self,
        aws_config,
        shared_instructions: Optional[str] = None,
        shared_files: Optional[List[str]] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> None:
        """Initialize the agency.

        Args:
            aws_config: AWS configuration for Bedrock
            shared_instructions (Optional[str]): Instructions shared by all agents
            shared_files (Optional[List[str]]): Files shared by all agents
            temperature (float): Default temperature for agents
            max_tokens (int): Default max tokens for agents
        """
        self.aws_config = aws_config
        self.shared_instructions = shared_instructions
        self.shared_files = shared_files or []
        self.temperature = temperature
        self.max_tokens = max_tokens

        self.agents: Dict[str, BedrockAgent] = {}
        self.threads: Dict[str, Thread] = {}
        self.agent_stats: Dict[str, Dict[str, Any]] = {}
        self.workflows: Dict[str, Workflow] = {}
        self.active_workflows: Dict[str, Dict[str, Any]] = {}
        self.shared_state: Dict[str, Any] = {}

    def create_thread(self, agent_name: Optional[str] = None) -> Thread:
        """Create a new thread.

        Args:
            agent_name (Optional[str]): Name of the agent to use for this thread

        Returns:
            Thread: The newly created thread
        """
        agent = self.agents.get(agent_name) if agent_name else None
        thread = Thread(agent)
        self.threads[thread.thread_id] = thread
        self.agent_stats[thread.thread_id] = {"messages": 0, "tokens": 0}
        return thread

    def get_thread(self, thread_id: str) -> Optional[Thread]:
        """Get a thread by ID.

        Args:
            thread_id (str): ID of the thread to get

        Returns:
            Optional[Thread]: The thread if found, None otherwise
        """
        return self.threads.get(thread_id)

    def _update_stats(self, thread_id: str, tokens: int) -> None:
        """Update usage statistics for a thread.

        Args:
            thread_id (str): ID of the thread
            tokens (int): Number of tokens used
        """
        if thread_id not in self.agent_stats:
            self.agent_stats[thread_id] = {"messages": 0, "tokens": 0}
        self.agent_stats[thread_id]["messages"] += 1
        self.agent_stats[thread_id]["tokens"] += tokens

    def get_stats(self, thread_id: str) -> Dict[str, int]:
        """Get usage statistics for a thread.

        Args:
            thread_id (str): ID of the thread

        Returns:
            Dict[str, int]: Usage statistics
        """
        return dict(self.agent_stats.get(thread_id, {}))

    def execute(
        self,
        thread_id: str,
        message: str,
        tool_results: Optional[List[ToolCallResult]] = None,
    ) -> ThreadMessage:
        """Execute a message in a thread.

        Args:
            thread_id (str): ID of the thread to execute in
            message (str): Message to execute
            tool_results (Optional[List[ToolCallResult]]): Results from previous tool calls

        Returns:
            ThreadMessage: Response message from the agent

        Raises:
            ValueError: If the thread does not exist or thread has no agent
        """
        thread = self.get_thread(thread_id)
        if not thread:
            raise ValueError(f"Thread {thread_id} does not exist")

        if not thread.agent:
            raise ValueError(f"Thread {thread_id} has no agent assigned")

        response = thread.execute(message, tool_results)
        self._update_stats(thread_id, thread.agent.last_token_count)
        return response

    def add_agent(
        self,
        name: str,
        model_id: str,
        instructions: Optional[str] = None,
        tools: Optional[List[BaseTool]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> BedrockAgent:
        """Add an agent to the agency.

        Args:
            name (str): Name of the agent
            model_id (str): Bedrock model ID
            instructions (Optional[str]): Agent-specific instructions
            tools (Optional[List[BaseTool]]): Tools for the agent
            temperature (Optional[float]): Temperature for model inference
            max_tokens (Optional[int]): Maximum tokens for model response

        Returns:
            BedrockAgent: The created agent

        Raises:
            ValueError: If an agent with the same name already exists
        """
        if name in self.agents:
            raise ValueError(f"Agent '{name}' already exists")

        agent = BedrockAgent(
            name=name,
            model_id=model_id,
            aws_config=self.aws_config,
            instructions=instructions or self.shared_instructions,
            temperature=temperature or self.temperature,
            max_tokens=max_tokens or self.max_tokens,
        )

        if tools:
            for tool in tools:
                agent.add_tool(tool)

        self.agents[name] = agent
        self.agent_stats[name] = {"messages": 0, "tokens": 0}
        return agent

    def create_workflow(self, name: str, steps: List[Dict[str, Any]]) -> str:
        """Create a new workflow.

        Args:
            name (str): Name of the workflow
            steps (List[Dict[str, Any]]): List of workflow steps

        Returns:
            str: ID of the created workflow

        Raises:
            ValueError: If a workflow with the same name already exists
        """
        if name in self.workflows:
            raise ValueError(f"Workflow '{name}' already exists")

        workflow_steps = []
        for step_data in steps:
            step = WorkflowStep(
                agent=step_data["agent"],
                instructions=step_data.get("instructions", ""),
                tools=step_data.get("tools", []),
                input_from=step_data.get("input_from", []),
                use_initial_input=step_data.get("use_initial_input", True),
                requires=step_data.get("requires", []),
            )
            workflow_steps.append(step)

        workflow = Workflow(name=name, steps=workflow_steps)
        self.workflows[name] = workflow
        return name

    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """Get a workflow by ID.

        Args:
            workflow_id (str): ID of the workflow to get

        Returns:
            Optional[Workflow]: The workflow if found, None otherwise
        """
        return self.workflows.get(workflow_id)

    def execute_workflow(
        self, workflow_id: str, input_data: Dict[str, Any]
    ) -> Dict[str, str]:
        """Execute a workflow.

        Args:
            workflow_id (str): ID of the workflow to execute
            input_data (Dict[str, Any]): Input data for the workflow

        Returns:
            Dict[str, str]: Results of the workflow execution, keyed by agent name

        Raises:
            ValueError: If the workflow does not exist or agent not found
        """
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow '{workflow_id}' does not exist")

        results = {}
        step_results = {}
        threads = {}

        for step in workflow.steps:
            agent = self.agents.get(step.agent)
            if not agent:
                raise ValueError(f"Agent '{step.agent}' not found")

            # Create thread for this step
            thread = self.create_thread(step.agent)
            threads[step.id] = thread

            # Prepare input message
            message = step.instructions + "\n\n"
            if step.use_initial_input:
                message += f"Input data: {input_data}\n\n"

            # Add results from dependent steps
            for dep_id in step.input_from:
                if dep_id in step_results:
                    message += f"Results from step {dep_id}: {step_results[dep_id]}\n\n"

            # Execute step
            response = thread.execute(agent, message)
            step_results[step.id] = response.content
            results[step.agent] = response.content

        return results

    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get the status of a workflow.

        Args:
            workflow_id (str): ID of the workflow

        Returns:
            Dict[str, Any]: Status of the workflow
        """
        return dict(self.active_workflows.get(workflow_id, {}))

    def get_agent_stats(self, agent_name: str) -> Dict[str, Any]:
        """Get statistics for an agent.

        Args:
            agent_name (str): Name of the agent

        Returns:
            Dict[str, Any]: Agent statistics
        """
        return self.agent_stats.get(agent_name, {})
