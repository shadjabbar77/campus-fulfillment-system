from typing import Any, Dict

from app.services.optimization_engine import optimize_order


def process_order_job(order: Dict[str, Any]) -> Dict[str, Any]:
    """
    RQ worker job.

    This function is executed outside the FastAPI request cycle.
    It runs the optimization engine and returns the assigned locker,
    route, ETA, and SLA result.
    """
    result = optimize_order(order)
    result["processed_by"] = "rq_worker"

    return result
