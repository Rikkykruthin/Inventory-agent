"""Mediator agent: synthesizes recommendations and makes final decision."""
import re
from .base import BaseAgent, AgentResponse


class MediatorAgent(BaseAgent):
    """Agent that synthesizes Conservative and Aggressive recommendations."""
    
    SYSTEM_PROMPT = """You are a CEO making the final inventory reorder decision.

YOUR OBJECTIVE: Balance cost efficiency with customer satisfaction.

CONTEXT: You have received recommendations from two advisors:
- Conservative Agent (CFO): Focused on minimizing costs and overstock risk
- Aggressive Agent (COO): Focused on maximizing availability and preventing stockouts

YOUR TASK:
1. Evaluate both recommendations and their reasoning
2. Assess which agent's concerns are more valid given the data
3. Make a final decision that balances both perspectives
4. Explain your reasoning transparently

DECISION FRAMEWORK:
- Don't just average the two recommendations — evaluate reasoning quality
- Consider the cost ratio: stockout cost vs holding cost (which is more expensive?)
- Look for unsupported assumptions (is there evidence for demand spikes?)
- Check the math (do the calculations make sense?)
- Consider business context (high-margin products favor availability, low-margin favor cost control)
- When uncertain, prefer the option with lower downside risk

WEIGHTED TOWARD OPTIONS:
- "conservative" — if you sided more with the Conservative agent's reasoning
- "aggressive" — if you sided more with the Aggressive agent's reasoning
- "balanced" — if you genuinely split the difference

OUTPUT FORMAT (you must follow this exactly):
QUANTITY: [number]
CONFIDENCE: [0.0 to 1.0]
WEIGHTED_TOWARD: [conservative|aggressive|balanced]
REASONING: [3-4 sentences explaining your decision, which agent's reasoning you weighted more and why]

Example:
QUANTITY: 90
CONFIDENCE: 0.80
WEIGHTED_TOWARD: conservative
REASONING: Conservative agent correctly identifies overstock risk, but underweights stockout cost ($15 vs $2.50 holding cost — 6× ratio). Aggressive agent correctly prioritizes availability but overestimates demand volatility (no evidence of spikes in data). Compromise: order 90 units to reach 135 total (11 days supply), which covers lead time + safety stock without excessive holding costs. Weighted toward conservative because the math supports a moderate buffer, not the aggressive 16-day supply.
"""
    
    def decide(
        self,
        inventory_data: str,
        conservative_rec: AgentResponse,
        aggressive_rec: AgentResponse
    ) -> dict:
        """Make final mediated decision.
        
        Args:
            inventory_data: Formatted inventory data string
            conservative_rec: Conservative agent's recommendation
            aggressive_rec: Aggressive agent's recommendation
            
        Returns:
            Dict with final decision and metadata
        """
        user_message = f"""{inventory_data}

CONSERVATIVE AGENT RECOMMENDATION:
Quantity: {conservative_rec['recommended_quantity']} units
Confidence: {conservative_rec['confidence']}
Reasoning: {conservative_rec['reasoning']}

AGGRESSIVE AGENT RECOMMENDATION:
Quantity: {aggressive_rec['recommended_quantity']} units
Confidence: {aggressive_rec['confidence']}
Reasoning: {aggressive_rec['reasoning']}

Based on both recommendations and the inventory data, provide your final decision.
"""
        
        response_text = self._call_ollama(self.SYSTEM_PROMPT, user_message)
        parsed = self._parse_response(response_text)
        
        # Return full decision with metadata
        return {
            "final_quantity": parsed["recommended_quantity"],
            "confidence": parsed["confidence"],
            "weighted_toward": parsed.get("weighted_toward", "balanced"),
            "reasoning": parsed["reasoning"]
        }
    
    def _parse_response(self, response_text: str) -> dict:
        """Parse Ollama's response into structured format.
        
        Args:
            response_text: Raw text response from Ollama
            
        Returns:
            Dict with parsed fields
        """
        # Extract quantity
        quantity_match = re.search(r'QUANTITY[:\s]+(\d+)', response_text, re.IGNORECASE)
        if not quantity_match:
            quantity_match = re.search(r'(?:order|recommend)\s+(\d+)\s+units', response_text, re.IGNORECASE)
        quantity = int(quantity_match.group(1)) if quantity_match else 80
        
        # Extract confidence
        confidence_match = re.search(r'CONFIDENCE[:\s]+(0?\.\d+|1\.0|0|1)', response_text, re.IGNORECASE)
        confidence = float(confidence_match.group(1)) if confidence_match else 0.80
        
        # Extract weighted_toward
        weighted_match = re.search(r'WEIGHTED_TOWARD[:\s]+(conservative|aggressive|balanced)', response_text, re.IGNORECASE)
        weighted_toward = weighted_match.group(1).lower() if weighted_match else "balanced"
        
        # Extract reasoning
        reasoning_match = re.search(r'REASONING[:\s]+(.+?)(?:\n\n|\Z)', response_text, re.DOTALL | re.IGNORECASE)
        if reasoning_match:
            reasoning = reasoning_match.group(1).strip()
        else:
            lines = response_text.split('\n')
            reasoning_lines = [l for l in lines if l.strip() and not l.strip().startswith(('QUANTITY', 'CONFIDENCE', 'WEIGHTED', 'REASONING'))]
            reasoning = ' '.join(reasoning_lines[:4]) if reasoning_lines else response_text[:250]
        
        return {
            "recommended_quantity": quantity,
            "confidence": confidence,
            "weighted_toward": weighted_toward,
            "reasoning": reasoning
        }
