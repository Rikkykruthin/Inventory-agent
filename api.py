"""FastAPI server for inventory reorder decision system."""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from orchestrator import InventoryOrchestrator
from data import InventoryData


# Load environment variables
load_dotenv()


# Pydantic models for request/response validation
class InventoryRequest(BaseModel):
    """Request model for inventory decision endpoint."""
    product_id: str = Field(..., description="Unique product identifier")
    product_name: str = Field(..., description="Product name")
    current_stock: int = Field(..., ge=0, description="Current stock on hand")
    sales_velocity: float = Field(..., gt=0, description="Units sold per day")
    lead_time_days: int = Field(..., gt=0, description="Days from order to delivery")
    holding_cost_per_unit: float = Field(..., ge=0, description="Cost per unit per month")
    stockout_cost_per_unit: float = Field(..., ge=0, description="Lost profit per missed sale")
    unit_cost: float = Field(..., gt=0, description="Cost to purchase one unit")
    safety_stock_days: int = Field(..., ge=0, description="Buffer stock in days")
    
    class Config:
        json_schema_extra = {
            "example": {
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
        }


class AgentRecommendation(BaseModel):
    """Agent recommendation model."""
    recommended_quantity: int
    confidence: float
    reasoning: str


class MediatorDecision(BaseModel):
    """Mediator decision model."""
    final_quantity: int
    confidence: float
    weighted_toward: str
    reasoning: str


class DecisionResponse(BaseModel):
    """Response model for inventory decision endpoint."""
    conservative_agent: AgentRecommendation
    aggressive_agent: AgentRecommendation
    mediator_agent: MediatorDecision
    metadata: dict


# Global orchestrator instance
orchestrator: InventoryOrchestrator | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown."""
    global orchestrator
    
    # Startup: Initialize orchestrator
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("⚠️  WARNING: GOOGLE_API_KEY not set. API calls will fail.")
    else:
        print("✅ Google API key loaded")
    
    orchestrator = InventoryOrchestrator(api_key)
    print("🚀 Inventory Agent System initialized")
    
    yield
    
    # Shutdown
    print("👋 Shutting down Inventory Agent System")


# Create FastAPI app
app = FastAPI(
    title="Inventory Reorder Decision System",
    description="Multi-agent AI system for inventory management decisions",
    version="0.1.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    """Root endpoint - redirect to docs."""
    return {
        "message": "Inventory Reorder Decision System API",
        "docs": "/docs",
        "demo": "/static/index.html"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    api_key_set = bool(os.getenv("GOOGLE_API_KEY"))
    return {
        "status": "healthy",
        "api_key_configured": api_key_set,
        "orchestrator_initialized": orchestrator is not None
    }


@app.post("/api/decide", response_model=DecisionResponse)
async def make_decision(request: InventoryRequest):
    """Make inventory reorder decision using multi-agent system.
    
    Args:
        request: Inventory data
        
    Returns:
        Decision response with all agent recommendations
        
    Raises:
        HTTPException: If orchestrator not initialized or API call fails
    """
    if orchestrator is None:
        raise HTTPException(
            status_code=500,
            detail="Orchestrator not initialized. Check server logs."
        )
    
    try:
        # Convert request to InventoryData dict
        inventory_data: InventoryData = {
            "product_id": request.product_id,
            "product_name": request.product_name,
            "current_stock": request.current_stock,
            "sales_velocity": request.sales_velocity,
            "lead_time_days": request.lead_time_days,
            "holding_cost_per_unit": request.holding_cost_per_unit,
            "stockout_cost_per_unit": request.stockout_cost_per_unit,
            "unit_cost": request.unit_cost,
            "safety_stock_days": request.safety_stock_days,
        }
        
        # Make decision
        decision = orchestrator.make_decision(inventory_data)
        
        return decision
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Decision failed: {str(e)}"
        )


# Mount static files (for HTML frontend)
app.mount("/static", StaticFiles(directory="static"), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
