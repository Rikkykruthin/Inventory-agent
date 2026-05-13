# Multi-Agent Inventory Decision System

A multi-agent AI system for inventory reorder decisions in retail and supply chain. Three specialized agents with different objectives debate and negotiate to produce optimal recommendations.

## Overview

Traditional inventory systems use fixed thresholds (reorder when stock < X). This approach ignores context, costs, and tradeoffs. This system uses three AI agents that explicitly debate the decision:

- **Conservative Agent (CFO mindset)** — Minimizes costs and overstock risk
- **Aggressive Agent (COO mindset)** — Maximizes availability and prevents stockouts  
- **Mediator Agent (CEO decision)** — Synthesizes both perspectives and makes final call

**Key insight:** A single LLM prompt asking "balance cost and availability" produces generic advice. Three agents with explicit objectives expose the tradeoff space and produce richer reasoning. The disagreement is the feature.

## Quick Start

```bash
# 1. Clone and setup
git clone https://github.com/Rikkykruthin/Inventory-agent.git
cd inventory-agent
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -e .

# 3. Configure environment
cp .env.example .env
# Edit .env and set OLLAMA_MODEL=llama2:latest

# 4. Run CLI demo
python main.py

# 5. Run API server
uvicorn api:app --reload

# 6. Open web interface
open http://localhost:8000/static/index.html
```

## Features

- ✅ **Multi-agent negotiation** — Agents genuinely disagree and debate
- ✅ **Transparent reasoning** — Explains every decision and tradeoff
- ✅ **REST API** — FastAPI with auto-generated documentation
- ✅ **Web interface** — Clean UI for non-technical users
- ✅ **Local execution** — Runs on Ollama, no cloud dependencies
- ✅ **Extensible** — Easy to add more agents or data sources

## Example Output

**Input:**
- Product: Organic Coffee Beans 1kg
- Current Stock: 45 units
- Sales Velocity: 12 units/day
- Lead Time: 7 days

**Agent Recommendations:**
- Conservative: 60 units (minimize costs)
- Aggressive: 240 units (prevent stockouts)
- **Final Decision: 80 units** (balanced approach, weighted toward conservative)

## Architecture

```
FastAPI Server (REST API + Web UI)
    ↓
Orchestrator (coordinates workflow)
    ↓
    ├→ Conservative Agent (minimize costs)
    ├→ Aggressive Agent (maximize availability)
    ↓
Mediator Agent (synthesize + decide)
    ↓
Ollama/Llama2 (local LLM)
```

## Project Structure

```
inventory-agent/
├── agents/              # Agent implementations
│   ├── base.py         # Base agent with Ollama integration
│   ├── conservative.py # Cost-minimization agent
│   ├── aggressive.py   # Availability-maximization agent
│   ├── mediator.py     # Synthesis agent
│   └── mock.py         # Mock agents for testing
├── data/               # Data models and mock data
│   └── inventory.py    # Inventory data structure
├── static/             # Web interface
│   └── index.html      # Single-page UI
├── orchestrator.py     # Agent coordination logic
├── api.py             # FastAPI server
├── main.py            # CLI interface
├── DESIGN.md          # Architecture and design decisions
└── README.md          # This file
```

## API Reference

### POST /api/decide

Make an inventory reorder decision.

**Request:**
```json
{
  "product_id": "SKU-12345",
  "product_name": "Organic Coffee Beans 1kg",
  "current_stock": 45,
  "sales_velocity": 12.0,
  "lead_time_days": 7,
  "holding_cost_per_unit": 2.50,
  "stockout_cost_per_unit": 15.00,
  "unit_cost": 8.00,
  "safety_stock_days": 3
}
```

**Response:**
```json
{
  "conservative_agent": {
    "recommended_quantity": 60,
    "confidence": 0.85,
    "reasoning": "Current stock covers 3.75 days..."
  },
  "aggressive_agent": {
    "recommended_quantity": 240,
    "confidence": 0.90,
    "reasoning": "Stockout risk is critical..."
  },
  "mediator_agent": {
    "final_quantity": 80,
    "confidence": 0.88,
    "weighted_toward": "conservative",
    "reasoning": "Conservative correctly identifies overstock risk..."
  },
  "metadata": {
    "timestamp": "2026-05-13T10:00:00Z",
    "model": "llama2:latest",
    "product_id": "SKU-12345"
  }
}
```

### GET /health

Check system health.

**Response:**
```json
{
  "status": "healthy",
  "api_key_configured": true,
  "orchestrator_initialized": true
}
```

## Design Decisions

**Why three agents instead of one prompt?**

Single prompts produce generic middle-ground advice. Three specialized agents expose the full tradeoff space:
- Explicit objectives (each agent has clear goals)
- Richer reasoning (three perspectives instead of one)
- Tunable system (adjust agent weights without rewriting prompts)
- Transparent tradeoffs (Mediator explains which factors dominated)

**Why Ollama instead of cloud APIs?**

Local execution means no API costs, no quota limits, and works offline. Good enough quality for proof-of-concept. 

**Alternative LLM Options:**
- **Google Gemini:** Set `GOOGLE_API_KEY` in `.env` (free tier available)
- **Anthropic Claude:** Set `ANTHROPIC_API_KEY` in `.env` (paid)
- **OpenAI GPT-4:** Set `OPENAI_API_KEY` in `.env` (paid)

Switch between providers by updating the base agent implementation in `agents/base.py`.

**Why direct orchestration instead of LangGraph/Agno?**

Frameworks add state management and error recovery but increase complexity. Direct orchestration (calling agents in sequence) is simpler to understand and debug. Can migrate to framework later if needed.

**Why mock data?**

Real inventory integration (Shopify, Square, NetSuite) adds API complexity without demonstrating the core agent reasoning logic. Mock data proves the concept and is easy to extend.

## Tech Stack

- **Backend:** Python 3.11+ with FastAPI
- **AI:** Ollama (Llama2) for local LLM execution (default)
  - Also supports: Google Gemini, Anthropic Claude, OpenAI GPT-4 (with API keys)
- **Frontend:** Vanilla HTML/CSS/JavaScript
- **Architecture:** Direct agent orchestration (no framework)

## Future Enhancements

**Learning Loop**
- Track decision outcomes (stockouts, overstock, costs)
- Feed historical performance back to agents
- Agents adjust confidence based on accuracy
- Meta-learning discovers patterns across product categories

**Multi-Product Optimization**
- Extend to portfolio of 50+ SKUs
- Agents negotiate across products simultaneously
- Optimize total inventory cost vs service level

**Real Inventory Integration**
- Connect to Shopify, Square, NetSuite APIs
- Pull real sales data and stock levels
- Push reorder recommendations back to system

**Human-in-the-Loop**
- High-stakes decisions require human approval
- Agents recommend, humans decide
- Track human overrides to improve agent reasoning

**Advanced Features**
- Real-time visualization of agent reasoning
- WebSocket updates for live decision tracking
- A/B testing framework (agent decisions vs rule-based)
- Explainability dashboard

## Testing

```bash
# Test CLI
python main.py

# Test API
curl -X POST http://localhost:8000/api/decide \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "SKU-99999",
    "product_name": "Test Product",
    "current_stock": 20,
    "sales_velocity": 8.0,
    "lead_time_days": 5,
    "holding_cost_per_unit": 1.50,
    "stockout_cost_per_unit": 20.00,
    "unit_cost": 12.00,
    "safety_stock_days": 2
  }'

# View API docs
open http://localhost:8000/docs
```

## Troubleshooting

**"GOOGLE_API_KEY not found" or similar errors**
→ Check your `.env` file and ensure `MOCK_MODE=false` and `OLLAMA_MODEL=llama2:latest`

**"ModuleNotFoundError"**
→ Install dependencies: `pip install -e .`

**"Address already in use"**
→ Kill existing server: `lsof -ti:8000 | xargs kill -9`

**Agents taking too long**
→ This is normal for local LLMs. Each decision takes ~30-40 seconds (3 sequential agent calls). Can optimize with parallel execution.

**Ollama not found**
→ Install Ollama from https://ollama.ai/ and run `ollama pull llama2`
