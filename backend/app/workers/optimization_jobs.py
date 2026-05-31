from typing import Any, Dict

from app.services.optimization_engine import optimize_order


def process_order_job(order: Dict[str, Any]) -> Dict[str, Any]:
    """
    Redis/RQ worker job.

    Runs the CampusFlow optimization engine outside the FastAPI request cycle.
    """
    result = optimize_order(order)
    result["processed_by"] = "rq_worker"

    return result
