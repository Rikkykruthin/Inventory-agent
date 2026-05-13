"""Conservative agent: minimizes costs and overstock risk."""
import re
from .base import BaseAgent, AgentResponse


class ConservativeAgent(BaseAgent):
    """Agent focused on minimizing holding costs and overstock risk."""
    
    SYSTEM_PROMPT = """You are a cost-conscious CFO making inventory reorder decisions.

YOUR OBJECTIVE: Minimize costs and avoid overstock risk.

PRIORITIES (in order):
1. Minimize holding costs (every unit in inventory costs money per month)
2. Avoid overstock (excess inventory ties up capital and may become obsolete)
3. Order just enough to cover lead time demand + minimal safety buffer
4. Prevent waste (especially for perishable goods)

DECISION FRAMEWORK:
- Calculate minimum viable order: lead time demand + small safety buffer
- Consider holding costs carefully ($ per unit per month adds up)
- Be skeptical of "what if demand spikes" arguments (data-driven, not fear-driven)
- Prefer smaller, more frequent orders over large bulk orders
- Remember: you can always order more if needed, but you can't un-order

OUTPUT FORMAT (you must follow this exactly):
QUANTITY: [number]
CONFIDENCE: [0.0 to 1.0]
REASONING: [2-3 sentences explaining your recommendation, citing specific numbers from the data]

Example:
QUANTITY: 50
CONFIDENCE: 0.75
REASONING: Current stock (45 units) covers 3.75 days of demand. With 7-day lead time, we need 84 units total (12/day × 7 days). Recommend ordering 50 units to reach 95 total, which includes a small safety buffer but avoids overstock risk. Holding costs are $2.50/unit/month, so minimizing excess inventory is critical.
"""
    
    def decide(self, inventory_data: str) -> AgentResponse:
        """Make conservative reorder recommendation.
        
        Args:
            inventory_data: Formatted inventory data string
            
        Returns:
            AgentResponse with conservative recommendation
        """
        user_message = f"""{inventory_data}

Based on this inventory data, provide your conservative reorder recommendation.
Focus on minimizing costs and avoiding overstock.
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
        quantity = int(quantity_match.group(1)) if quantity_match else 50
        
        # Extract confidence
        confidence_match = re.search(r'CONFIDENCE[:\s]+(0?\.\d+|1\.0|0|1)', response_text, re.IGNORECASE)
        confidence = float(confidence_match.group(1)) if confidence_match else 0.75
        
        # Extract reasoning - try to get the REASONING section or the whole response
        reasoning_match = re.search(r'REASONING[:\s]+(.+?)(?:\n\n|\Z)', response_text, re.DOTALL | re.IGNORECASE)
        if reasoning_match:
            reasoning = reasoning_match.group(1).strip()
        else:
            # If no REASONING label, take everything after the confidence or quantity
            lines = response_text.split('\n')
            reasoning_lines = [l for l in lines if l.strip() and not l.strip().startswith(('QUANTITY', 'CONFIDENCE', 'REASONING'))]
            reasoning = ' '.join(reasoning_lines[:3]) if reasoning_lines else response_text[:200]
        
        return AgentResponse(
            recommended_quantity=quantity,
            confidence=confidence,
            reasoning=reasoning
        )
