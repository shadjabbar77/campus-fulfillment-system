from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.optimization_engine import optimize_order


router = APIRouter(prefix="/optimization", tags=["optimization"])


class OptimizeOrderRequest(BaseModel):
    id: Optional[int] = None
    destination: str = Field(..., example="Brock Commons")
    priority: str = Field(..., example="express")
    size: str = Field(..., example="medium")
    deadline_minutes: int = Field(..., gt=0, example=25)


def request_to_order(request: OptimizeOrderRequest) -> Dict[str, Any]:
    if hasattr(request, "model_dump"):
        return request.model_dump()
    return request.dict()


@router.get("/health")
def optimization_health() -> Dict[str, str]:
    return {
        "status": "ok",
        "service": "campusflow-optimization",
    }


@router.post("/orders")
def optimize_order_sync(request: OptimizeOrderRequest) -> Dict[str, Any]:
    order = request_to_order(request)

    try:
        return optimize_order(order)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
