"""Aggressive agent: maximizes availability and prevents stockouts."""
import re
from .base import BaseAgent, AgentResponse


class AggressiveAgent(BaseAgent):
    """Agent focused on maximizing product availability and preventing stockouts."""
    
    SYSTEM_PROMPT = """You are a customer-obsessed COO making inventory reorder decisions.

YOUR OBJECTIVE: Maximize product availability and prevent stockouts at all costs.

PRIORITIES (in order):
1. Never run out of stock (stockouts damage customer trust and lose sales)
2. Build safety buffers for demand variability and supply chain delays
3. Account for worst-case scenarios (demand spikes, delayed shipments)
4. Prioritize customer satisfaction over holding costs
5. Remember: a lost sale is gone forever, but excess inventory can be sold later

DECISION FRAMEWORK:
- Calculate generous order: lead time demand + substantial safety buffer
- Consider stockout costs carefully ($ per missed sale, plus brand damage)
- Take demand uncertainty seriously (what if sales increase?)
- Account for supply chain risk (what if delivery is delayed?)
- Prefer having too much over having too little

OUTPUT FORMAT (you must follow this exactly):
QUANTITY: [number]
CONFIDENCE: [0.0 to 1.0]
REASONING: [2-3 sentences explaining your recommendation, citing specific numbers from the data]

Example:
QUANTITY: 150
CONFIDENCE: 0.85
REASONING: Stockout cost is $15/unit vs holding cost of $2.50/unit/month — losing a sale is 6× more expensive than holding stock for a month. Current stock only covers 3.75 days, which is dangerously low. Recommend ordering 150 units to reach 195 total (16 days of supply), ensuring we never run out even if demand spikes or lead time extends.
"""
    
    def decide(self, inventory_data: str) -> AgentResponse:
        """Make aggressive reorder recommendation.
        
        Args:
            inventory_data: Formatted inventory data string
            
        Returns:
            AgentResponse with aggressive recommendation
        """
        user_message = f"""{inventory_data}

Based on this inventory data, provide your aggressive reorder recommendation.
Focus on maximizing availability and preventing stockouts.
"""
        
        response_text = self._call_ollama(self.SYSTEM_PROMPT, user_message)
        return self._parse_response(response_text)
    
    def _parse_response(self, response_text: str) -> AgentResponse:
        """Parse Ollama's response into structured format.
        
        Args:
            response_text: Raw text response from Ollama
            
        Returns:
            Structured AgentResponse
        """
        # Extract quantity - try multiple patterns
        quantity_match = re.search(r'QUANTITY[:\s]+(\d+)', response_text, re.IGNORECASE)
        if not quantity_match:
            quantity_match = re.search(r'recommend(?:ing)?\s+(?:ordering\s+)?(\d+)\s+units', response_text, re.IGNORECASE)
        quantity = int(quantity_match.group(1)) if quantity_match else 100
        
        # Extract confidence
        confidence_match = re.search(r'CONFIDENCE[:\s]+(0?\.\d+|1\.0|0|1)', response_text, re.IGNORECASE)
        confidence = float(confidence_match.group(1)) if confidence_match else 0.85
        
        # Extract reasoning
        reasoning_match = re.search(r'REASONING[:\s]+(.+?)(?:\n\n|\Z)', response_text, re.DOTALL | re.IGNORECASE)
        if reasoning_match:
            reasoning = reasoning_match.group(1).strip()
        else:
            lines = response_text.split('\n')
            reasoning_lines = [l for l in lines if l.strip() and not l.strip().startswith(('QUANTITY', 'CONFIDENCE', 'REASONING'))]
            reasoning = ' '.join(reasoning_lines[:3]) if reasoning_lines else response_text[:200]
        
        return AgentResponse(
            recommended_quantity=quantity,
            confidence=confidence,
            reasoning=reasoning
        )
