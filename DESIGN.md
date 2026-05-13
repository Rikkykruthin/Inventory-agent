# Design: Multi-Agent Inventory Decision System

## The Problem

Inventory management is a constant tug-of-war between two goals:
- **Minimize costs** — don't overstock, reduce holding costs
- **Maximize availability** — never run out, keep customers happy

Rule-based systems (reorder when stock < X) are too rigid. They ignore context like lead time variability, demand spikes, or cost ratios. I wanted something that could reason about tradeoffs explicitly.

## The Core Idea

Instead of asking one LLM to "balance cost and availability" (which just produces safe, generic advice), I gave three agents explicitly different objectives and let them disagree.

**The disagreement is the feature.**

- **Conservative Agent (CFO)** — minimize costs, avoid overstock
- **Aggressive Agent (COO)** — maximize availability, prevent stockouts
- **Mediator Agent (CEO)** — evaluate both arguments, make the final call

The Mediator doesn't average the two numbers. It reads both reasonings, checks which argument is better supported by the data, and decides. That synthesis is where the value is.

## Architecture

```
Inventory Data
    ↓
Orchestrator
    ├→ Conservative Agent  ─┐
    ├→ Aggressive Agent    ─┤→ Mediator Agent → Final Decision
```

Conservative and Aggressive run first (they're independent), then Mediator gets both outputs and decides.

All three agents call a local Ollama model. No cloud APIs, no costs, works offline.

## Key Design Decisions

**No framework (LangGraph, Agno, etc.)**
Direct orchestration is simpler to read and debug. Three sequential function calls. Can always add a framework later if state management becomes necessary.

**Local LLM via Ollama**
No API keys, no rate limits, runs offline. Slower (~30-40s per decision) but fine for this use case. Swapping to a cloud model is a one-line change in `base.py`.

**Mock mode**
`MOCK_MODE=true` in `.env` returns hardcoded responses instantly. Useful for testing the API and UI without waiting on the LLM.

**Regex parsing with fallbacks**
LLMs don't always follow output formats exactly. Each agent tries to parse structured fields (QUANTITY, CONFIDENCE, REASONING) and falls back gracefully if the format drifts.

## Data Flow

**Input** (per product):
```
current_stock, sales_velocity, lead_time_days,
holding_cost_per_unit, stockout_cost_per_unit, unit_cost, safety_stock_days
```

**Output**:
```
conservative_agent: { recommended_quantity, confidence, reasoning }
aggressive_agent:   { recommended_quantity, confidence, reasoning }
mediator_agent:     { final_quantity, confidence, weighted_toward, reasoning }
```

`weighted_toward` tells you whether the Mediator sided with conservative, aggressive, or split the difference — useful for understanding why the final number landed where it did.

## What I'd Do Differently

- **Async execution** — Conservative and Aggressive could run truly in parallel with `asyncio`. Currently sequential despite being independent.
- **Outcome tracking** — Log actual results (did we stockout? did we overstock?) and feed that back to improve agent confidence over time.
- **Real data** — Mock inventory data proves the concept but connecting to a real source (Shopify, Square) is the obvious next step.
