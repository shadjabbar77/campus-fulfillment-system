import copy
from typing import Any, Dict, List, Optional

from app.services.campus_data import build_campus_graph, build_lockers
from app.services.locker_assignment import assign_best_locker
from app.services.pathfinding import Graph


Order = Dict[str, Any]
Locker = Dict[str, Any]
OptimizationResult = Dict[str, Any]

DELIVERY_SPEED_M_PER_MIN = 80
HANDOFF_TIME_MIN = 4

SUPPORTED_PRIORITIES = {"express", "standard"}
SUPPORTED_SIZES = {"small", "medium", "large"}


def estimate_delivery_minutes(distance_m: float) -> float:
    """
    Estimate delivery time from walking distance.

    Includes a fixed handoff time plus walking time.
    """
    return round(HANDOFF_TIME_MIN + (distance_m / DELIVERY_SPEED_M_PER_MIN), 2)


def normalize_order(order: Order, graph: Graph) -> Order:
    """
    Validate and normalize an incoming order dictionary.
    """
    required_fields = ["destination", "priority", "size", "deadline_minutes"]

    for field in required_fields:
        if field not in order:
            raise ValueError(f"Order must include '{field}'.")

    destination = str(order["destination"]).strip()
    priority = str(order["priority"]).lower().strip()
    size = str(order["size"]).lower().strip()

    if destination not in graph:
        raise ValueError(f"Destination '{destination}' does not exist in the campus graph.")

    if priority not in SUPPORTED_PRIORITIES:
        raise ValueError(
            f"Unsupported priority '{priority}'. Expected one of: {sorted(SUPPORTED_PRIORITIES)}"
        )

    if size not in SUPPORTED_SIZES:
        raise ValueError(
            f"Unsupported package size '{size}'. Expected one of: {sorted(SUPPORTED_SIZES)}"
        )

    try:
        deadline_minutes = int(order["deadline_minutes"])
    except ValueError as exc:
        raise ValueError("deadline_minutes must be an integer.") from exc

    if deadline_minutes <= 0:
        raise ValueError("deadline_minutes must be greater than 0.")

    return {
        "id": order.get("id"),
        "destination": destination,
        "priority": priority,
        "size": size,
        "deadline_minutes": deadline_minutes,
    }


def get_sla_status(estimated_delivery_minutes: float, deadline_minutes: int) -> str:
    if estimated_delivery_minutes <= deadline_minutes:
        return "on_time"

    return "late"


def optimize_order(
    order: Order,
    lockers: Optional[List[Locker]] = None,
    graph: Optional[Graph] = None,
) -> OptimizationResult:
    """
    Optimize a single campus package order.

    The engine:
    1. Validates the order.
    2. Selects the best eligible locker.
    3. Computes shortest route from locker to destination.
    4. Estimates delivery time.
    5. Evaluates SLA status.
    """
    campus_graph = graph if graph is not None else build_campus_graph()
    locker_snapshot = copy.deepcopy(lockers if lockers is not None else build_lockers())

    normalized_order = normalize_order(order, campus_graph)

    assignment = assign_best_locker(
        order=normalized_order,
        lockers=locker_snapshot,
        graph=campus_graph,
    )

    assigned_locker = assignment["locker"]
    distance_m = float(assignment["distance_m"])
    estimated_minutes = estimate_delivery_minutes(distance_m)
    sla_status = get_sla_status(
        estimated_delivery_minutes=estimated_minutes,
        deadline_minutes=normalized_order["deadline_minutes"],
    )

    return {
        "order_id": normalized_order.get("id"),
        "status": "assigned",
        "destination": normalized_order["destination"],
        "priority": normalized_order["priority"],
        "size": normalized_order["size"],
        "deadline_minutes": normalized_order["deadline_minutes"],
        "assigned_locker_id": assigned_locker["id"],
        "assigned_locker_name": assigned_locker["name"],
        "assigned_locker_location": assigned_locker["location_node"],
        "route": assignment["route"],
        "distance_m": round(distance_m, 2),
        "estimated_delivery_minutes": estimated_minutes,
        "sla_status": sla_status,
        "decision_score": round(float(assignment["score"]), 2),
    }
