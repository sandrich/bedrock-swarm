"""Thread implementation for managing conversations.

A Thread represents a single conversation flow between a user and an agent.
It maintains the conversation history and handles message processing.
"""

import json
from datetime import datetime
from typing import Dict, List, Literal, Optional, Tuple
from uuid import uuid4

from ..agents.base import BedrockAgent
from ..memory.base import Message
from ..types import AgentResponse, ToolCall, ToolOutput, ToolResult


class Run:
    """Represents a single execution run in a thread."""

    def __init__(self) -> None:
        """Initialize a new run."""
        self.id = str(uuid4())
        self.status: Literal[
            "queued", "in_progress", "requires_action", "completed", "failed"
        ] = "queued"
        self.started_at = datetime.now()
        self.completed_at: Optional[datetime] = None
        self.required_action: Optional[Dict] = None
        self.last_error: Optional[str] = None

    def complete(self) -> None:
        """Mark the run as completed."""
        self.status = "completed"
        self.completed_at = datetime.now()

    def fail(self, error: str) -> None:
        """Mark the run as failed."""
        self.status = "failed"
        self.last_error = error
        self.completed_at = datetime.now()

    def require_action(self, action: Dict) -> None:
        """Set the run to require action."""
        self.status = "requires_action"
        self.required_action = action


class Thread:
    """A Thread manages a single conversation between a user and an agent.

    The Thread is responsible for:
    1. Maintaining conversation history
    2. Processing messages through the agent
    3. Handling tool executions
    4. Recording all interactions
    5. Managing runs and their states
    """

    def __init__(self, agent: BedrockAgent) -> None:
        """Initialize a new thread.

        Args:
            agent: The agent that will process messages in this thread
        """
        self.id = str(uuid4())
        self.agent = agent
        self.history: List[Message] = []
        self.created_at = datetime.now()
        self.last_message_at: Optional[datetime] = None
        self.current_run: Optional[Run] = None
        self.runs: List[Run] = []
        self.event_system = None  # Will be set by Agency

    def process_message(self, content: str) -> str:
        """Process a message through this thread.

        This method:
        1. Records the incoming message
        2. Creates and tracks a new run
        3. Processes it through the agent
        4. Handles any tool executions
        5. Records and returns the response

        Args:
            content: The message to process

        Returns:
            The final response text
        """
        # Create new run
        self.current_run = Run()
        self.runs.append(self.current_run)
        self.current_run.status = "in_progress"

        # Create agent start event
        agent_start_id = self.event_system.create_event(
            type="agent_start",
            agent_name=self.agent.name,
            run_id=self.current_run.id,
            thread_id=self.id,
            details={"message": content},
        )
        self.event_system.start_event_scope(agent_start_id)

        try:
            # Get initial response from agent
            response = self.agent.generate(content)

            # Handle potential tool calls
            if response.get("tool_calls"):
                # Set run status for tool execution
                self.current_run.require_action(
                    {"type": "tool_calls", "tool_calls": response["tool_calls"]}
                )

                # Execute tools and get final response
                tool_outputs = self._execute_tools(response["tool_calls"])

                # Get final response incorporating tool results
                final_response = self._get_final_response(content, tool_outputs)
                response_text = final_response["content"]

            else:
                # Use direct response if no tool call
                response_text = response["content"]

            # Create agent complete event
            self.event_system.create_event(
                type="agent_complete",
                agent_name=self.agent.name,
                run_id=self.current_run.id,
                thread_id=self.id,
                details={"response": response_text},
            )

            # Mark run as completed
            self.current_run.complete()

        except Exception as e:
            # Handle any errors
            error_msg = str(e)
            if self.current_run:
                self.current_run.fail(error_msg)

            # Create error event
            self.event_system.create_event(
                type="error",
                agent_name=self.agent.name,
                run_id=self.current_run.id,
                thread_id=self.id,
                details={"error": error_msg},
            )

            response_text = f"Error processing message: {error_msg}"

        finally:
            self.event_system.end_event_scope()

        return response_text

    def _execute_tools(self, tool_calls: List[ToolCall]) -> List[ToolOutput]:
        """Execute a list of tool calls.

        Args:
            tool_calls: List of tool calls to execute

        Returns:
            List of tool outputs
        """
        tool_outputs = []

        for tool_call in tool_calls:
            # Create tool start event
            tool_start_id = self.event_system.create_event(
                type="tool_start",
                agent_name=self.agent.name,
                run_id=self.current_run.id if self.current_run else "none",
                thread_id=self.id,
                details={
                    "tool_name": tool_call["function"]["name"],
                    "arguments": tool_call["function"]["arguments"],
                },
            )
            self.event_system.start_event_scope(tool_start_id)

            try:
                # Execute the tool
                result = self._execute_single_tool(tool_call)
                execution_metadata = {
                    "success": result["success"],
                    "result": result["result"] if result["success"] else None,
                    "error": result["error"] if not result["success"] else None,
                }

                # Create tool complete event
                self.event_system.create_event(
                    type="tool_complete",
                    agent_name=self.agent.name,
                    run_id=self.current_run.id if self.current_run else "none",
                    thread_id=self.id,
                    details={
                        "tool_name": tool_call["function"]["name"],
                        "result": result["result"]
                        if result["success"]
                        else result["error"],
                        "success": result["success"],
                    },
                )

                # Add to outputs
                tool_outputs.append(
                    {
                        "tool_call_id": tool_call["id"],
                        "output": result["result"]
                        if result["success"]
                        else f"Error: {result['error']}",
                        "execution_metadata": execution_metadata,
                    }
                )

            finally:
                self.event_system.end_event_scope()

        return tool_outputs

    def _execute_single_tool(self, tool_call: ToolCall) -> ToolResult:
        """Execute a single tool call.

        Args:
            tool_call: The tool call to execute

        Returns:
            Result of the tool execution
        """
        tool_name = tool_call["function"]["name"]

        # Check if tool exists
        if tool_name not in self.agent.tools:
            return {
                "success": False,
                "result": "",
                "error": f"Tool {tool_name} not found",
            }

        try:
            # Parse arguments - handle both string and dict formats for backward compatibility
            args = tool_call['function']['arguments']
            if isinstance(args, str):
                args = json.loads(args)

            # Get and execute tool
            tool = self.agent.tools[tool_name]
            result = tool.execute(**args, thread=self)

            return {"success": True, "result": str(result), "error": None}
        except Exception as e:
            return {"success": False, "result": "", "error": str(e)}

    def _get_final_response(
        self, original_message: str, tool_outputs: List[ToolOutput]
    ) -> Dict[str, str]:
        """Get final response after tool execution.

        Args:
            original_message: The original user message
            tool_outputs: Results from tool execution

        Returns:
            Final response from the agent
        """
        # Format tool results
        tool_results = "\n".join(
            f"Tool {output['tool_call_id']} returned: {output['output']}"
            for output in tool_outputs
        )

        # Get final response
        return self.agent.model.invoke(
            client=self.agent.session.client("bedrock-runtime"),
            message=f"{tool_results}\nPlease provide a natural response to the original question: {original_message}",
            system="You are providing a natural response based on the tool results.",
        )

    def _record_message(
        self, role: str, content: str, metadata: Optional[Dict] = None
    ) -> None:
        """Record a message in the thread history.

        Args:
            role: The role of the message sender (user/assistant/system)
            content: The message content
            metadata: Optional metadata about the message
        """
        now = datetime.now()

        # Ensure metadata includes basic timing information
        if metadata is None:
            metadata = {}

        metadata.update(
            {
                "timestamp": now.isoformat(),
                "thread_id": self.id,
                "run_id": self.current_run.id if self.current_run else None,
            }
        )

        self.history.append(
            Message(role=role, content=content, timestamp=now, metadata=metadata)
        )
        self.last_message_at = now

    def get_history(self) -> List[Message]:
        """Get the complete message history.

        Returns:
            List of all messages in chronological order
        """
        return self.history.copy()

    def get_last_message(self) -> Optional[Message]:
        """Get the most recent message.

        Returns:
            The last message or None if history is empty
        """
        return self.history[-1] if self.history else None

    def get_context_window(self, n: int = 5) -> List[Message]:
        """Get the n most recent messages.

        Args:
            n: Number of messages to return

        Returns:
            List of up to n most recent messages
        """
        return self.history[-n:] if self.history else []

    def get_run(self, run_id: str) -> Optional[Run]:
        """Get a specific run by ID.

        Args:
            run_id: ID of the run to retrieve

        Returns:
            The run if found, None otherwise
        """
        return next((run for run in self.runs if run.id == run_id), None)

    def get_current_run(self) -> Optional[Run]:
        """Get the current run.

        Returns:
            The current run if one exists
        """
        return self.current_run

    def cancel_run(self, run_id: str) -> bool:
        """Cancel a specific run.

        Args:
            run_id: ID of the run to cancel

        Returns:
            True if run was cancelled, False otherwise
        """
        run = self.get_run(run_id)
        if run and run.status in ["queued", "in_progress", "requires_action"]:
            run.fail("Run cancelled by user")
            return True
        return False

    @property
    def thread_id(self) -> str:
        """Get the thread ID.

        Returns:
            str: Thread ID
        """
        return self.id
