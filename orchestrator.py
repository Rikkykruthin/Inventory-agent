"""Orchestrator for multi-agent inventory decision system."""
import os
from datetime import datetime
from typing import TypedDict

from agents import ConservativeAgent, AggressiveAgent, MediatorAgent, AgentResponse
from data import InventoryData, format_inventory_for_prompt


class DecisionResponse(TypedDict):
    """Complete decision response with all agent outputs."""
    conservative_agent: AgentResponse
    aggressive_agent: AgentResponse
    mediator_agent: dict
    metadata: dict


class InventoryOrchestrator:
    """Orchestrates the three-agent decision process."""
    
    def __init__(self, api_key: str | None = None, mock_mode: bool = False):
        """Initialize orchestrator with all three agents.
        
        Args:
            api_key: Anthropic API key. If None, reads from environment.
            mock_mode: If True, use mock agents instead of real API calls.
        """
        self.mock_mode = mock_mode or os.getenv("MOCK_MODE", "false").lower() == "true"
        
        if self.mock_mode:
            print("⚠️  Running in MOCK MODE (no API calls)")
            from agents.mock import MockConservativeAgent, MockAggressiveAgent, MockMediatorAgent
            self.conservative = MockConservativeAgent()
            self.aggressive = MockAggressiveAgent()
            self.mediator = MockMediatorAgent()
        else:
            self.conservative = ConservativeAgent(api_key)
            self.aggressive = AggressiveAgent(api_key)
            self.mediator = MediatorAgent(api_key)
    
    def make_decision(self, inventory_data: InventoryData) -> DecisionResponse:
        """Execute full decision process with all three agents.
        
        Args:
            inventory_data: Inventory data dict
            
        Returns:
            DecisionResponse with all agent outputs and metadata
        """
        # Format data for agents
        formatted_data = format_inventory_for_prompt(inventory_data)
        
        # Step 1: Get Conservative recommendation
        print("🔵 Conservative Agent analyzing...")
        conservative_rec = self.conservative.decide(formatted_data)
        print(f"   → Recommends: {conservative_rec['recommended_quantity']} units "
              f"(confidence: {conservative_rec['confidence']:.2f})")
        
        # Step 2: Get Aggressive recommendation
        print("🔴 Aggressive Agent analyzing...")
        aggressive_rec = self.aggressive.decide(formatted_data)
        print(f"   → Recommends: {aggressive_rec['recommended_quantity']} units "
              f"(confidence: {aggressive_rec['confidence']:.2f})")
        
        # Step 3: Mediator makes final decision
        print("⚖️  Mediator Agent synthesizing...")
        mediator_decision = self.mediator.decide(
            formatted_data,
            conservative_rec,
            aggressive_rec
        )
        print(f"   → Final decision: {mediator_decision['final_quantity']} units "
              f"(weighted toward: {mediator_decision['weighted_toward']})")
        
        # Compile full response
        return DecisionResponse(
            conservative_agent=conservative_rec,
            aggressive_agent=aggressive_rec,
            mediator_agent=mediator_decision,
            metadata={
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "model": "mock" if self.mock_mode else os.getenv("OLLAMA_MODEL", "gemma4:latest"),
                "product_id": inventory_data["product_id"],
                "product_name": inventory_data["product_name"]
            }
        )
