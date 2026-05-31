import os
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from redis import Redis
from rq import Queue
from rq.exceptions import NoSuchJobError
from rq.job import Job

from app.services.campus_data import build_campus_graph, build_lockers
from app.services.optimization_engine import optimize_order
from app.workers.optimization_jobs import process_order_job


router = APIRouter(prefix="/optimization", tags=["optimization"])

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
FULFILLMENT_QUEUE_NAME = os.getenv("FULFILLMENT_QUEUE_NAME", "fulfillment")

redis_connection = Redis.from_url(REDIS_URL)
fulfillment_queue = Queue(FULFILLMENT_QUEUE_NAME, connection=redis_connection)


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


@router.get("/campus")
def get_campus_data() -> Dict[str, Any]:
    graph = build_campus_graph()
    lockers = build_lockers()

    return {
        "nodes": list(graph.keys()),
        "edge_count": sum(len(edges) for edges in graph.values()) // 2,
        "lockers": lockers,
    }


@router.post("/orders")
def optimize_order_sync(request: OptimizeOrderRequest) -> Dict[str, Any]:
    order = request_to_order(request)

    try:
        return optimize_order(order)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/jobs")
def enqueue_optimization_job(request: OptimizeOrderRequest) -> Dict[str, Any]:
    order = request_to_order(request)

    try:
        job = fulfillment_queue.enqueue(process_order_job, order)
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="Could not enqueue optimization job. Make sure Redis is running.",
        ) from exc

    return {
        "job_id": job.id,
        "status": job.get_status(),
        "queue": FULFILLMENT_QUEUE_NAME,
        "message": "Order queued for asynchronous optimization.",
    }


@router.get("/jobs/{job_id}")
def get_optimization_job(job_id: str) -> Dict[str, Any]:
    try:
        job = Job.fetch(job_id, connection=redis_connection)
    except NoSuchJobError as exc:
        raise HTTPException(status_code=404, detail="Job not found.") from exc

    return {
        "job_id": job.id,
        "status": job.get_status(refresh=True),
        "result": job.result,
        "error": job.exc_info,
    }
