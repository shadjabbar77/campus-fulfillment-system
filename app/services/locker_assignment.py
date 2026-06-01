from typing import Any, Dict, List

from app.services.pathfinding import Graph, shortest_path


Locker = Dict[str, Any]
Order = Dict[str, Any]


def _locker_can_accept_order(locker: Locker, order: Order) -> bool:
    """
    Check whether a locker has capacity and can accept this package size.
    """
    capacity = locker.get("capacity", 0)
    current_load = locker.get("current_load", 0)

    if capacity <= 0:
        return False

    if current_load >= capacity:
        return False

    if order.get("size") == "large" and not locker.get("accepts_large_packages", False):
        return False

    return True


def assign_best_locker(order: Order, lockers: List[Locker], graph: Graph) -> Dict[str, Any]:
    """
    Assign the best locker for an order using distance, capacity, and priority.

    The score rewards nearby lockers and penalizes lockers that are close to full.

    Returns:
        {
            "locker": locker,
            "distance_m": distance,
            "route": route,
            "score": score
        }
    """
    if "destination" not in order:
        raise ValueError("Order must include a destination.")

    best_assignment = None
    best_score = float("inf")

    for locker in lockers:
        if not _locker_can_accept_order(locker, order):
            continue

        location_node = locker.get("location_node")
        if location_node is None:
            continue

        try:
            distance_m, route = shortest_path(
                graph=graph,
                start=location_node,
                goal=order["destination"],
            )
        except ValueError:
            continue

        capacity_ratio = locker["current_load"] / locker["capacity"]
        capacity_penalty = capacity_ratio * 200

        priority_bonus = -100 if order.get("priority") == "express" else 0

        score = distance_m + capacity_penalty + priority_bonus

        if score < best_score:
            best_score = score
            best_assignment = {
                "locker": locker,
                "distance_m": distance_m,
                "route": route,
                "score": score,
            }

    if best_assignment is None:
        raise ValueError("No eligible locker found for this order.")

    return best_assignment
