import json
from typing import Any, Dict, List, Optional, Union

import boto3

from ..config import AWSConfig
from ..tools.base import BaseTool

class BedrockAgent:
    """Base class for Bedrock-powered agents.
    
    Args:
        name (str): Name of the agent
        model_id (str): Bedrock model ID (e.g., anthropic.claude-v2)
        aws_config (AWSConfig): AWS configuration
        instructions (Optional[str]): System instructions for the agent
        temperature (Optional[float]): Temperature for model inference
        max_tokens (Optional[int]): Maximum tokens for model response
    """
    
    def __init__(
        self,
        name: str,
        model_id: str,
        aws_config: AWSConfig,
        instructions: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ):
        self.name = name
        self.model_id = model_id
        self.instructions = instructions
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.tools: List[BaseTool] = []
        
        self.bedrock = boto3.client(
            'bedrock-runtime',
            region_name=aws_config.region,
            profile_name=aws_config.profile,
            endpoint_url=aws_config.endpoint_url
        )
    
    def add_tool(self, tool: BaseTool) -> None:
        """Add a tool to the agent.
        
        Args:
            tool (BaseTool): Tool to add
        """
        self.tools.append(tool)
    
    def _format_claude_prompt(self, message: str) -> str:
        """Format prompt for Claude models.
        
        Args:
            message (str): User message
            
        Returns:
            str: Formatted prompt
        """
        system = f"System: {self.instructions}\n\n" if self.instructions else ""
        return f"{system}Human: {message}\n\nAssistant:"
    
    def _format_prompt(self, message: str) -> str:
        """Format prompt based on model type.
        
        Args:
            message (str): User message
            
        Returns:
            str: Formatted prompt
        """
        if self.model_id.startswith("anthropic.claude"):
            return self._format_claude_prompt(message)
        # Add support for other models here
        return message
    
    def _get_tool_schemas(self) -> List[Dict[str, Any]]:
        """Get schemas for all tools.
        
        Returns:
            List[Dict[str, Any]]: List of tool schemas
        """
        return [tool.get_schema() for tool in self.tools]
    
    async def invoke(self, message: str) -> str:
        """Invoke the Bedrock model.
        
        Args:
            message (str): Message to send to the model
            
        Returns:
            str: Model response
        """
        # Format the prompt based on model type
        prompt = self._format_prompt(message)
        
        # Prepare request body
        body = {
            "prompt": prompt,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
        
        if self.tools:
            body["tools"] = self._get_tool_schemas()
        
        # Invoke the model
        response = self.bedrock.invoke_model(
            modelId=self.model_id,
            body=json.dumps(body)
        )
        
        # Parse response
        response_body = json.loads(response["body"].read())
        
        if response_body.get("stop_reason") == "tool_call":
            # Handle tool calls
            tool_calls = response_body.get("tool_calls", [])
            results = []
            
            for call in tool_calls:
                tool_name = call["name"]
                tool = next((t for t in self.tools if t.name == tool_name), None)
                if tool:
                    result = await tool.execute(**call["parameters"])
                    results.append(result)
            
            return "\n".join([response_body["completion"]] + results)
        
        return response_body["completion"]
    
    async def process_message(self, message: str, **kwargs: Any) -> str:
        """Process a message and return a response.
        
        Args:
            message (str): Message to process
            **kwargs: Additional arguments
            
        Returns:
            str: Agent's response
        """
        return await self.invoke(message) 