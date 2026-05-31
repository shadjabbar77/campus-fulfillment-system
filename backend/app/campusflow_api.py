from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.services.optimization_engine import optimize_order


app = FastAPI(title="CampusFlow Optimization API")


class OptimizeOrderRequest(BaseModel):
    id: Optional[int] = None
    destination: str = Field(..., example="Brock Commons")
    priority: str = Field(..., example="express")
    size: str = Field(..., example="medium")
    deadline_minutes: int = Field(..., gt=0, example=25)


@app.get("/optimization/health")
def optimization_health() -> Dict[str, str]:
    return {
        "status": "ok",
        "service": "campusflow-optimization",
    }


@app.post("/optimization/orders")
def optimize_order_endpoint(request: OptimizeOrderRequest) -> Dict[str, Any]:
    if hasattr(request, "model_dump"):
        order = request.model_dump()
    else:
        order = request.dict()

    try:
        return optimize_order(order)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
