"""Base agent class for Ollama local LLM interaction."""
import os
from typing import TypedDict
import ollama


class AgentResponse(TypedDict):
    """Standard response format for all agents."""
    recommended_quantity: int
    confidence: float
    reasoning: str


class BaseAgent:
    """Base class for all inventory decision agents."""
    
    def __init__(self, api_key: str | None = None):
        """Initialize agent with Ollama client.
        
        Args:
            api_key: Not used for Ollama (kept for compatibility)
        """
        self.model = os.getenv("OLLAMA_MODEL", "gemma4:latest")
        print(f"🤖 Using Ollama model: {self.model}")
    
    def _call_ollama(self, system_prompt: str, user_message: str) -> str:
        """Make API call to Ollama.
        
        Args:
            system_prompt: System prompt defining agent role and objectives
            user_message: User message with inventory data and request
            
        Returns:
            Ollama's response text
        """
        try:
            response = ollama.chat(
                model=self.model,
                messages=[
                    {
                        'role': 'system',
                        'content': system_prompt
                    },
                    {
                        'role': 'user',
                        'content': user_message
                    }
                ],
                options={
                    'temperature': 0.7,
                    'num_predict': 300,
                }
            )
            return response['message']['content']
        except Exception as e:
            raise RuntimeError(f"Ollama API call failed: {e}")
    
    def decide(self, inventory_data: str) -> AgentResponse:
        """Make a reorder decision based on inventory data.
        
        Args:
            inventory_data: Formatted inventory data string
            
        Returns:
            AgentResponse with recommendation, confidence, and reasoning
            
        Raises:
            NotImplementedError: Must be implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement decide()")
