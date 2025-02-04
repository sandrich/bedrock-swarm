from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import UUID, uuid4

from ..agents.base import BedrockAgent
from ..memory.base import BaseMemory, Message, SimpleMemory

class Swarm:
    """A swarm of coordinated agents.
    
    Args:
        memory (Optional[BaseMemory]): Memory system to use
        max_rounds (Optional[int]): Maximum conversation rounds
    """
    
    def __init__(
        self,
        memory: Optional[BaseMemory] = None,
        max_rounds: Optional[int] = None
    ):
        self.memory = memory or SimpleMemory()
        self.max_rounds = max_rounds
        self.agents: Dict[UUID, BedrockAgent] = {}
        self._round = 0
    
    def add_agent(self, agent: BedrockAgent) -> UUID:
        """Add an agent to the swarm.
        
        Args:
            agent (BedrockAgent): Agent to add
            
        Returns:
            UUID: Unique ID for the agent
        """
        agent_id = uuid4()
        self.agents[agent_id] = agent
        return agent_id
    
    def get_agent(self, agent_id: UUID) -> Optional[BedrockAgent]:
        """Get an agent by ID.
        
        Args:
            agent_id (UUID): Agent ID
            
        Returns:
            Optional[BedrockAgent]: The agent if found
        """
        return self.agents.get(agent_id)
    
    def remove_agent(self, agent_id: UUID) -> bool:
        """Remove an agent from the swarm.
        
        Args:
            agent_id (UUID): Agent ID
            
        Returns:
            bool: True if agent was removed
        """
        if agent_id in self.agents:
            del self.agents[agent_id]
            return True
        return False
    
    async def broadcast(
        self,
        message: str,
        exclude: Optional[List[UUID]] = None
    ) -> List[str]:
        """Broadcast a message to all agents.
        
        Args:
            message (str): Message to broadcast
            exclude (Optional[List[UUID]]): Agent IDs to exclude
            
        Returns:
            List[str]: List of agent responses
        """
        exclude = exclude or []
        responses = []
        
        for agent_id, agent in self.agents.items():
            if agent_id not in exclude:
                response = await agent.process_message(message)
                responses.append(response)
                
                # Store in memory
                await self.memory.add_message(Message(
                    role="human",
                    content=message,
                    timestamp=datetime.now(),
                    metadata={"agent_id": str(agent_id)}
                ))
                await self.memory.add_message(Message(
                    role="assistant",
                    content=response,
                    timestamp=datetime.now(),
                    metadata={"agent_id": str(agent_id)}
                ))
        
        return responses
    
    async def discuss(
        self,
        topic: str,
        rounds: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Have agents discuss a topic.
        
        Args:
            topic (str): Topic to discuss
            rounds (Optional[int]): Number of discussion rounds
            
        Returns:
            List[Dict[str, Any]]: Discussion history
        """
        rounds = rounds or self.max_rounds or 3
        history = []
        
        # Initial round
        responses = await self.broadcast(topic)
        history.append({
            "round": 0,
            "topic": topic,
            "responses": responses
        })
        
        # Discussion rounds
        for i in range(1, rounds):
            self._round = i
            
            # Each agent responds to previous round
            round_responses = []
            prev_responses = history[-1]["responses"]
            
            for agent_id, agent in self.agents.items():
                context = "\n".join([
                    f"Previous responses:",
                    *[f"- {r}" for r in prev_responses],
                    f"\nWhat are your thoughts on the discussion so far?"
                ])
                
                response = await agent.process_message(context)
                round_responses.append(response)
                
                await self.memory.add_message(Message(
                    role="assistant",
                    content=response,
                    timestamp=datetime.now(),
                    metadata={
                        "agent_id": str(agent_id),
                        "round": i
                    }
                ))
            
            history.append({
                "round": i,
                "responses": round_responses
            })
        
        return history 