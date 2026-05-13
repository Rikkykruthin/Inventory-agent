#!/usr/bin/env python3
"""CLI interface for inventory reorder decision system."""
import os
import sys
from dotenv import load_dotenv

from orchestrator import InventoryOrchestrator
from data import SAMPLE_INVENTORY


def print_header():
    """Print CLI header."""
    print("\n" + "="*70)
    print("  INVENTORY REORDER DECISION SYSTEM")
    print("  Multi-Agent AI System: Conservative → Aggressive → Mediator")
    print("="*70 + "\n")


def print_inventory_summary(data):
    """Print inventory data summary."""
    print("📦 INVENTORY DATA")
    print(f"   Product: {data['product_name']} ({data['product_id']})")
    print(f"   Current stock: {data['current_stock']} units")
    print(f"   Sales velocity: {data['sales_velocity']} units/day")
    print(f"   Lead time: {data['lead_time_days']} days")
    print(f"   Holding cost: ${data['holding_cost_per_unit']:.2f}/unit/month")
    print(f"   Stockout cost: ${data['stockout_cost_per_unit']:.2f}/unit")
    print()


def print_agent_response(agent_name: str, emoji: str, response: dict):
    """Print individual agent response."""
    print(f"{emoji} {agent_name.upper()}")
    print(f"   Recommendation: {response['recommended_quantity']} units")
    print(f"   Confidence: {response['confidence']:.2f}")
    print(f"   Reasoning: {response['reasoning']}")
    print()


def print_mediator_response(response: dict):
    """Print mediator's final decision."""
    print("⚖️  MEDIATOR (FINAL DECISION)")
    print(f"   Final order quantity: {response['final_quantity']} units")
    print(f"   Confidence: {response['confidence']:.2f}")
    print(f"   Weighted toward: {response['weighted_toward']}")
    print(f"   Reasoning: {response['reasoning']}")
    print()


def print_summary(decision):
    """Print decision summary."""
    print("="*70)
    print("📊 DECISION SUMMARY")
    print(f"   Conservative recommended: {decision['conservative_agent']['recommended_quantity']} units")
    print(f"   Aggressive recommended: {decision['aggressive_agent']['recommended_quantity']} units")
    print(f"   Final decision: {decision['mediator_agent']['final_quantity']} units")
    print(f"   Decision timestamp: {decision['metadata']['timestamp']}")
    print("="*70 + "\n")


def main():
    """Run CLI demo."""
    # Load environment variables
    load_dotenv()
    
    # Check for API key
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ ERROR: GOOGLE_API_KEY not found")
        print("   Please set your API key:")
        print("   1. Copy .env.example to .env")
        print("   2. Add your Google API key to .env")
        print("   3. Run this script again")
        sys.exit(1)
    
    # Print header
    print_header()
    
    # Print inventory data
    print_inventory_summary(SAMPLE_INVENTORY)
    
    # Initialize orchestrator
    print("🚀 Initializing multi-agent system...\n")
    orchestrator = InventoryOrchestrator()
    
    # Make decision
    try:
        decision = orchestrator.make_decision(SAMPLE_INVENTORY)
        print()
        
        # Print detailed results
        print_agent_response(
            "Conservative Agent",
            "🔵",
            decision["conservative_agent"]
        )
        
        print_agent_response(
            "Aggressive Agent",
            "🔴",
            decision["aggressive_agent"]
        )
        
        print_mediator_response(decision["mediator_agent"])
        
        # Print summary
        print_summary(decision)
        
        print("✅ Decision complete! All agents have provided their recommendations.\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("   Check your API key and internet connection.")
        sys.exit(1)


if __name__ == "__main__":
    main()
