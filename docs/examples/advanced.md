# Advanced Examples

This guide shows advanced usage patterns of Bedrock Swarm.

## Multi-Agent System

Example of multiple agents working together:

```python
from bedrock_swarm import Agency, BedrockAgent
from bedrock_swarm.config import AWSConfig
from bedrock_swarm.tools.web import WebSearchTool

def main():
    # Configure AWS
    config = AWSConfig(
        region="us-west-2",
        profile="default"
    )

    # Create agency
    agency = Agency(aws_config=config)

    # Add specialized agents
    agency.add_agent(
        name="researcher",
        model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        instructions="You are a research specialist. Use web search to find information.",
        tools=[WebSearchTool()]
    )

    agency.add_agent(
        name="analyst",
        model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        instructions="You are a data analyst. Analyze information and identify patterns."
    )

    # Create thread and execute task
    thread = agency.create_thread("researcher")
    response = thread.execute("Research recent developments in quantum computing")
    print(f"Research results: {response.content}")

    # Pass to analyst
    thread = agency.create_thread("analyst")
    response = thread.execute(f"Analyze these findings: {response.content}")
    print(f"Analysis: {response.content}")

if __name__ == "__main__":
    main()
```

## Custom Tools

Example of creating and using custom tools:

```python
from typing import List, Dict
from bedrock_swarm import BedrockAgent
from bedrock_swarm.tools.base import BaseTool

class DataCollector(BaseTool):
    @property
    def name(self) -> str:
        return "data_collector"

    @property
    def description(self) -> str:
        return "Collects data from a source"

    def get_schema(self):
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "source": {
                        "type": "string",
                        "description": "Data source to collect from"
                    }
                },
                "required": ["source"]
            }
        }

    def _execute_impl(self, source: str) -> List[Dict]:
        # Implementation
        return [{"data": f"Sample data from {source}"}]

class DataAnalyzer(BaseTool):
    @property
    def name(self) -> str:
        return "data_analyzer"

    @property
    def description(self) -> str:
        return "Analyzes collected data"

    def get_schema(self):
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "data": {
                        "type": "array",
                        "description": "Data to analyze"
                    }
                },
                "required": ["data"]
            }
        }

    def _execute_impl(self, data: List[Dict]) -> Dict:
        # Implementation
        return {"analysis": f"Analysis of {len(data)} data points"}

def main():
    # Configure AWS
    config = AWSConfig(
        region="us-west-2",
        profile="default"
    )

    # Create agent with custom tools
    agent = BedrockAgent(
        name="data_scientist",
        model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        aws_config=config,
        instructions="You are a data scientist. Use tools to collect and analyze data."
    )

    agent.add_tool(DataCollector())
    agent.add_tool(DataAnalyzer())

    # Execute task using tools
    response = agent.process_message("Collect and analyze data from source X")
    print(response)

if __name__ == "__main__":
    main()
```

## Workflow Orchestration

Example of creating and executing workflows:

```python
from bedrock_swarm import Agency
from bedrock_swarm.config import AWSConfig

def main():
    # Configure AWS
    config = AWSConfig(
        region="us-west-2",
        profile="default"
    )

    # Create agency
    agency = Agency(aws_config=config)

    # Create workflow
    workflow_id = agency.create_workflow(
        name="research_workflow",
        steps=[
            {
                "agent": "researcher",
                "instructions": "Research the topic",
                "tools": ["web_search"]
            },
            {
                "agent": "analyst",
                "instructions": "Analyze the findings",
                "input_from": ["step1"]
            },
            {
                "agent": "writer",
                "instructions": "Write a report",
                "input_from": ["step1", "step2"]
            }
        ]
    )

    # Execute workflow
    results = agency.execute_workflow(
        workflow_id=workflow_id,
        input_data={"topic": "AI safety"}
    )

    # Get workflow status
    status = agency.get_workflow_status(workflow_id)
    print(f"Workflow status: {status}")
    print(f"Results: {results}")

if __name__ == "__main__":
    main()
```

## Advanced Error Handling

Example of advanced error handling and retries:

```python
from bedrock_swarm import BedrockAgent
from bedrock_swarm.exceptions import ModelInvokeError, ToolError
from bedrock_swarm.tools.base import BaseTool

class RiskAssessor(BaseTool):
    @property
    def name(self) -> str:
        return "risk_assessor"

    @property
    def description(self) -> str:
        return "Assesses risk level of a task"

    def get_schema(self):
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "task": {
                        "type": "string",
                        "description": "Task to evaluate"
                    }
                },
                "required": ["task"]
            }
        }

    def _execute_impl(self, task: str) -> float:
        # Implementation
        return 0.7  # Risk score between 0 and 1

def main():
    # Configure AWS
    config = AWSConfig(
        region="us-west-2",
        profile="default"
    )

    # Create agent with risk assessment
    agent = BedrockAgent(
        name="safety_agent",
        model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        aws_config=config,
        instructions="You are a safety-conscious AI assistant."
    )

    agent.add_tool(RiskAssessor())

    try:
        # Process message with risk assessment
        response = agent.process_message("Execute this potentially risky task")
        print(response)
    except ModelInvokeError as e:
        print(f"Model error: {e}")
        # Handle model errors (e.g., retry with different parameters)
    except ToolError as e:
        print(f"Tool error: {e}")
        # Handle tool errors (e.g., try alternative tool)
    except Exception as e:
        print(f"Unexpected error: {e}")
        # Log error and notify administrators

if __name__ == "__main__":
    main()
```
