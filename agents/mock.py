"""Mock agents for demo purposes when API quota is exhausted."""
import re
from .base import AgentResponse


class MockConservativeAgent:
    """Mock conservative agent that returns pre-defined responses."""
    
    def decide(self, inventory_data: str) -> AgentResponse:
        """Return mock conservative recommendation based on input."""
        # Extract current stock from inventory data
        stock_match = re.search(r'Stock on hand:\s*(\d+)', inventory_data)
        velocity_match = re.search(r'Sales velocity:\s*([\d.]+)', inventory_data)
        lead_time_match = re.search(r'Lead time:\s*(\d+)', inventory_data)
        
        current_stock = int(stock_match.group(1)) if stock_match else 45
        velocity = float(velocity_match.group(1)) if velocity_match else 12
        lead_time = int(lead_time_match.group(1)) if lead_time_match else 7
        
        # Conservative calculation: lead time demand + small buffer
        lead_time_demand = velocity * lead_time
        recommended = int(lead_time_demand * 0.9)  # 90% of lead time demand
        days_of_stock = current_stock / velocity
        
        return AgentResponse(
            recommended_quantity=recommended,
            confidence=0.85,
            reasoning=f"Current stock ({current_stock} units) covers {days_of_stock:.1f} days of demand. With {lead_time}-day lead time, we need {lead_time_demand:.0f} units total ({velocity}/day × {lead_time} days). Recommend ordering {recommended} units to minimize holding costs while covering essential demand. Holding costs must be kept low to maintain profitability."
        )


class MockAggressiveAgent:
    """Mock aggressive agent that returns pre-defined responses."""
    
    def decide(self, inventory_data: str) -> AgentResponse:
        """Return mock aggressive recommendation based on input."""
        # Extract data
        stock_match = re.search(r'Stock on hand:\s*(\d+)', inventory_data)
        velocity_match = re.search(r'Sales velocity:\s*([\d.]+)', inventory_data)
        lead_time_match = re.search(r'Lead time:\s*(\d+)', inventory_data)
        safety_match = re.search(r'Safety stock target:\s*(\d+)', inventory_data)
        
        current_stock = int(stock_match.group(1)) if stock_match else 45
        velocity = float(velocity_match.group(1)) if velocity_match else 12
        lead_time = int(lead_time_match.group(1)) if lead_time_match else 7
        safety_stock = int(safety_match.group(1)) if safety_match else 36
        
        # Aggressive calculation: lead time demand + safety stock + buffer
        lead_time_demand = velocity * lead_time
        recommended = int(lead_time_demand + safety_stock * 1.5)  # Extra safety buffer
        days_of_stock = current_stock / velocity
        total_days = (current_stock + recommended) / velocity
        
        return AgentResponse(
            recommended_quantity=recommended,
            confidence=0.90,
            reasoning=f"Current stock only covers {days_of_stock:.1f} days - dangerously low! Stockout risk is critical with {lead_time}-day lead time. Recommend ordering {recommended} units to reach {current_stock + recommended} total ({total_days:.0f} days of supply), ensuring we never run out even if demand spikes or delivery delays occur. Lost sales are far more expensive than holding costs."
        )


class MockMediatorAgent:
    """Mock mediator agent that returns pre-defined responses."""
    
    def decide(self, inventory_data: str, conservative_rec: AgentResponse, aggressive_rec: AgentResponse) -> dict:
        """Return mock mediator decision based on both recommendations."""
        # Calculate a balanced decision
        conservative_qty = conservative_rec['recommended_quantity']
        aggressive_qty = aggressive_rec['recommended_quantity']
        
        # Weighted average (60% aggressive, 40% conservative)
        final_qty = int(conservative_qty * 0.4 + aggressive_qty * 0.6)
        
        # Determine which way we're leaning
        diff_from_conservative = abs(final_qty - conservative_qty)
        diff_from_aggressive = abs(final_qty - aggressive_qty)
        
        if diff_from_conservative < diff_from_aggressive:
            weighted = "conservative"
            explanation = f"Conservative agent's risk assessment is more aligned with current data. While stockout prevention is important, the {conservative_qty}-unit recommendation undervalues availability. Aggressive agent's {aggressive_qty}-unit suggestion overestimates volatility."
        elif diff_from_aggressive < diff_from_conservative:
            weighted = "aggressive"
            explanation = f"Aggressive agent correctly prioritizes customer availability. Conservative agent's {conservative_qty}-unit recommendation underweights stockout costs. However, {aggressive_qty} units may be excessive given stable demand patterns."
        else:
            weighted = "balanced"
            explanation = f"Both agents present valid concerns. Conservative's {conservative_qty}-unit focus on cost control and Aggressive's {aggressive_qty}-unit emphasis on availability both have merit."
        
        return {
            "final_quantity": final_qty,
            "confidence": 0.88,
            "weighted_toward": weighted,
            "reasoning": f"{explanation} Final decision: order {final_qty} units to balance cost efficiency with service level requirements."
        }
