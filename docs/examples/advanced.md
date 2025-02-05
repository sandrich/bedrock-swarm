# Advanced Usage Examples

This guide demonstrates advanced usage patterns of Bedrock Swarm.

## Multi-Agent Systems

Example of multiple agents working together:

```python
from bedrock_swarm import Agent, AgentGroup

async def main():
    # Create specialized agents
    researcher = Agent(
        name="researcher",
        system_prompt="You are a research agent that finds and analyzes information."
    )
    
    writer = Agent(
        name="writer",
        system_prompt="You are a writing agent that creates clear and engaging content."
    )
    
    editor = Agent(
        name="editor",
        system_prompt="You are an editing agent that improves and refines content."
    )
    
    # Create agent group
    team = AgentGroup([researcher, writer, editor])
    
    # Collaborate on a task
    result = await team.collaborate(
        "Create a comprehensive article about quantum computing"
    )
    
    print(result)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

## Custom Tool Chain

Example of creating a chain of tools:

```python
from bedrock_swarm import Agent, Tool
from typing import List, Dict

class DataFetcher(Tool):
    name = "data_fetcher"
    description = "Fetches data from various sources"
    
    async def run(self, source: str) -> List[Dict]:
        # Implementation
        pass

class DataProcessor(Tool):
    name = "data_processor"
    description = "Processes and transforms data"
    
    async def run(self, data: List[Dict]) -> List[Dict]:
        # Implementation
        pass

class DataAnalyzer(Tool):
    name = "data_analyzer"
    description = "Analyzes processed data"
    
    async def run(self, data: List[Dict]) -> Dict:
        # Implementation
        pass

async def main():
    # Create agent with tool chain
    agent = Agent(
        name="data_analyst",
        tools=[
            DataFetcher(),
            DataProcessor(),
            DataAnalyzer()
        ]
    )
    
    # Use the tool chain
    result = await agent.run(
        "Fetch data from our database, process it, and provide an analysis"
    )
    
    print(result)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

## Advanced Memory Usage

Example of using vector store memory with persistence:

```python
from bedrock_swarm import Agent

async def main():
    # Create agent with advanced memory
    agent = Agent(
        name="knowledge_base",
        memory_config={
            "type": "vectorstore",
            "embedding_model": "amazon.titan-embed-text-v1",
            "persistence": {
                "enabled": True,
                "path": "knowledge_base.json"
            }
        }
    )
    
    # Store complex information
    await agent.run("Store this fact: The speed of light is approximately 299,792,458 meters per second")
    
    # Perform semantic search
    result = await agent.memory.search(
        "What is the speed of light?",
        k=1
    )
    
    print(result)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

## Custom Agent Implementation

Example of creating a custom agent class:

```python
from bedrock_swarm import Agent
from typing import Any, Dict, Optional

class SpecializedAgent(Agent):
    def __init__(
        self,
        name: str,
        expertise: str,
        confidence_threshold: float = 0.8,
        **kwargs: Any
    ):
        super().__init__(name=name, **kwargs)
        self.expertise = expertise
        self.confidence_threshold = confidence_threshold
    
    async def evaluate_confidence(self, task: str) -> float:
        # Implementation
        pass
    
    async def run(
        self,
        input: str,
        **kwargs: Any
    ) -> Optional[str]:
        confidence = await self.evaluate_confidence(input)
        
        if confidence < self.confidence_threshold:
            return f"I am not confident enough to handle this task (confidence: {confidence})"
        
        return await super().run(input, **kwargs)

async def main():
    # Create specialized agent
    expert = SpecializedAgent(
        name="math_expert",
        expertise="mathematics",
        confidence_threshold=0.9
    )
    
    # Test with different queries
    math_query = "Solve the quadratic equation x² + 2x + 1 = 0"
    history_query = "Who won the 100 Years War?"
    
    print(await expert.run(math_query))
    print(await expert.run(history_query))

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
``` 