"""Workflow implementation for managing agent tasks."""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set

from ..tools.base import BaseTool


@dataclass
class WorkflowStep:
    """A step in a workflow.

    Attributes:
        agent (str): Name of the agent to execute this step
        instructions (Optional[str]): Step-specific instructions
        tools (Optional[List[BaseTool]]): Tools to use for this step
        input_from (Optional[List[str]]): Agent names to get input from
        use_initial_input (bool): Whether to use workflow's initial input
        requires (Optional[List[str]]): Steps that must complete before this one
    """

    agent: str
    instructions: Optional[str] = None
    tools: Optional[List[BaseTool]] = None
    input_from: Optional[List[str]] = None
    use_initial_input: bool = True
    requires: Optional[List[str]] = None


class Workflow:
    """Workflow class for managing sequences of agent tasks."""

    def __init__(self, name: str, steps: List[WorkflowStep]):
        """Initialize a workflow.

        Args:
            name (str): Unique workflow name
            steps (List[WorkflowStep]): Steps in the workflow

        Raises:
            ValueError: If workflow configuration is invalid
        """
        self.name = name
        self.steps = steps
        self.validate_workflow()

    def validate_workflow(self) -> None:
        """Validate workflow configuration.

        Raises:
            ValueError: If workflow configuration is invalid
        """
        # Check for duplicate agent names
        agent_names = [step.agent for step in self.steps]
        if len(agent_names) != len(set(agent_names)):
            raise ValueError("Duplicate agent names in workflow")

        # Validate dependencies
        for step in self.steps:
            if step.input_from:
                # Check that input sources exist
                invalid_sources = set(step.input_from) - set(agent_names)
                if invalid_sources:
                    raise ValueError(
                        f"Invalid input sources for {step.agent}: {invalid_sources}"
                    )

            if step.requires:
                # Check that required steps exist
                invalid_deps = set(step.requires) - set(agent_names)
                if invalid_deps:
                    raise ValueError(
                        f"Invalid dependencies for {step.agent}: {invalid_deps}"
                    )

                # Check for circular dependencies
                if step.agent in step.requires:
                    raise ValueError(
                        f"Circular dependency: {step.agent} requires itself"
                    )

    def get_execution_plan(self) -> List[WorkflowStep]:
        """Generate an execution plan for the workflow.

        Returns:
            List[WorkflowStep]: Ordered list of steps to execute

        This method:
        1. Builds a dependency graph
        2. Performs topological sort
        3. Returns steps in execution order
        """
        # Build dependency graph
        graph: Dict[str, Set[str]] = {
            step.agent: set(step.requires or []) for step in self.steps
        }

        # Find all nodes
        nodes = set(graph.keys())

        # Track processed nodes and execution order
        processed: Set[str] = set()
        execution_order: List[str] = []

        def process_node(node: str, path: Set[str]) -> None:
            """Process a node in the dependency graph.

            Args:
                node (str): Node to process
                path (Set[str]): Current path in graph traversal

            Raises:
                ValueError: If circular dependency is detected
            """
            if node in path:
                raise ValueError(f"Circular dependency detected: {' -> '.join(path)}")

            if node in processed:
                return

            path.add(node)

            # Process dependencies
            for dep in graph[node]:
                process_node(dep, path)

            path.remove(node)
            processed.add(node)
            execution_order.append(node)

        # Process all nodes
        for node in nodes:
            if node not in processed:
                process_node(node, set())

        # Convert order back to steps
        step_map = {step.agent: step for step in self.steps}
        return [step_map[agent] for agent in execution_order]

    def get_step(self, agent_name: str) -> Optional[WorkflowStep]:
        """Get a step by agent name.

        Args:
            agent_name (str): Name of the agent

        Returns:
            Optional[WorkflowStep]: The step if found
        """
        for step in self.steps:
            if step.agent == agent_name:
                return step
        return None

    def add_step(self, step: WorkflowStep, validate: bool = True) -> None:
        """Add a step to the workflow.

        Args:
            step (WorkflowStep): Step to add
            validate (bool): Whether to validate after adding

        Raises:
            ValueError: If step is invalid or creates invalid workflow
        """
        self.steps.append(step)
        if validate:
            self.validate_workflow()

    def remove_step(self, agent_name: str, validate: bool = True) -> bool:
        """Remove a step from the workflow.

        Args:
            agent_name (str): Name of the agent
            validate (bool): Whether to validate after removing

        Returns:
            bool: True if step was removed

        Raises:
            ValueError: If removing step creates invalid workflow
        """
        original_len = len(self.steps)
        self.steps = [s for s in self.steps if s.agent != agent_name]

        if validate and len(self.steps) != original_len:
            self.validate_workflow()

        return len(self.steps) != original_len

    def to_dict(self) -> Dict[str, Any]:
        """Convert workflow to dictionary.

        Returns:
            Dict[str, Any]: Workflow as dictionary
        """
        return {
            "name": self.name,
            "steps": [
                {
                    "agent": step.agent,
                    "instructions": step.instructions,
                    "tools": [tool.__class__.__name__ for tool in (step.tools or [])],
                    "input_from": step.input_from,
                    "use_initial_input": step.use_initial_input,
                    "requires": step.requires,
                }
                for step in self.steps
            ],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Workflow":
        """Create workflow from dictionary.

        Args:
            data (Dict[str, Any]): Workflow data

        Returns:
            Workflow: Created workflow
        """
        steps = []
        for step_data in data["steps"]:
            # Note: Tool instances would need to be created/looked up
            # based on the tool class names
            step = WorkflowStep(
                agent=step_data["agent"],
                instructions=step_data.get("instructions"),
                tools=None,  # Tools need to be created separately
                input_from=step_data.get("input_from"),
                use_initial_input=step_data.get("use_initial_input", True),
                requires=step_data.get("requires"),
            )
            steps.append(step)

        return cls(name=data["name"], steps=steps)
