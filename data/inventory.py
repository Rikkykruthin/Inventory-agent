"""Mock inventory data for demo purposes."""
from typing import TypedDict


class InventoryData(TypedDict):
    """Inventory data structure."""
    product_id: str
    product_name: str
    current_stock: int
    sales_velocity: float
    lead_time_days: int
    holding_cost_per_unit: float
    stockout_cost_per_unit: float
    unit_cost: float
    safety_stock_days: int


# Sample inventory data for demo
SAMPLE_INVENTORY: InventoryData = {
    "product_id": "SKU-12345",
    "product_name": "Organic Coffee Beans 1kg",
    "current_stock": 45,  # units on hand
    "sales_velocity": 12.0,  # units per day (average over last 30 days)
    "lead_time_days": 7,  # days from order to delivery
    "holding_cost_per_unit": 2.50,  # $ per unit per month
    "stockout_cost_per_unit": 15.00,  # $ lost profit per missed sale
    "unit_cost": 8.00,  # $ cost to purchase one unit
    "safety_stock_days": 3,  # buffer stock (days of demand)
}


def format_inventory_for_prompt(data: InventoryData) -> str:
    """Format inventory data as readable text for LLM prompts."""
    days_of_stock = data["current_stock"] / data["sales_velocity"]
    lead_time_demand = data["sales_velocity"] * data["lead_time_days"]
    safety_stock_units = data["sales_velocity"] * data["safety_stock_days"]
    
    return f"""
PRODUCT: {data['product_name']} ({data['product_id']})

CURRENT STATE:
- Stock on hand: {data['current_stock']} units
- Days of stock remaining: {days_of_stock:.1f} days
- Sales velocity: {data['sales_velocity']} units/day (30-day average)

SUPPLY CHAIN:
- Lead time: {data['lead_time_days']} days
- Lead time demand: {lead_time_demand:.0f} units (sales during lead time)
- Safety stock target: {safety_stock_units:.0f} units ({data['safety_stock_days']} days buffer)

COSTS:
- Unit cost: ${data['unit_cost']:.2f}
- Holding cost: ${data['holding_cost_per_unit']:.2f} per unit per month
- Stockout cost: ${data['stockout_cost_per_unit']:.2f} per missed sale

CALCULATIONS:
- Total stock needed: {lead_time_demand + safety_stock_units:.0f} units (lead time demand + safety stock)
- Current gap: {(lead_time_demand + safety_stock_units - data['current_stock']):.0f} units
""".strip()
