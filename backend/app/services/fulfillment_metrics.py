import copy
import random
from statistics import mean
from typing import Any, Dict, List, Tuple

from app.services.campus_data import build_campus_graph, build_lockers
from app.services.locker_assignment import assign_best_locker
from app.services.pathfinding import Graph, shortest_path
from app.services.priority_scheduler import OrderPriorityScheduler


Locker = Dict[str, Any]
Order = Dict[str, Any]
Assignment = Dict[str, Any]

DELIVERY_SPEED_M_PER_MIN = 80
HANDOFF_TIME_MIN = 4
DEFAULT_ORDER_COUNT = 1000
DEFAULT_RANDOM_SEED = 42


def generate_orders(count: int, seed: int = DEFAULT_RANDOM_SEED) -> List[Order]:
    random.seed(seed)

    destinations = [
        "Brock Commons",
        "Koerner Library",
        "Buchanan",
        "Sauder",
        "Place Vanier",
        "Totem Park",
        "Exchange Residence",
        "Thunderbird Residence",
        "Engineering",
        "Bookstore",
    ]

    orders: List[Order] = []

    for order_id in range(1, count + 1):
        priority = random.choices(
            ["express", "standard"],
            weights=[0.25, 0.75],
            k=1,
        )[0]

        size = random.choices(
            ["small", "medium", "large"],
            weights=[0.50, 0.40, 0.10],
            k=1,
        )[0]

        if priority == "express":
            deadline_minutes = random.randint(12, 30)
        else:
            deadline_minutes = random.randint(45, 120)

        orders.append(
            {
                "id": order_id,
                "destination": random.choice(destinations),
                "priority": priority,
                "size": size,
                "deadline_minutes": deadline_minutes,
            }
        )

    return orders


def schedule_orders(orders: List[Order]) -> List[Order]:
    scheduler = OrderPriorityScheduler()

    for order in orders:
        scheduler.add_order(order)

    scheduled_orders: List[Order] = []

    while not scheduler.is_empty():
        next_order = scheduler.pop_next_order()

        if next_order is not None:
            scheduled_orders.append(next_order)

    return scheduled_orders


def locker_can_accept_order(locker: Locker, order: Order) -> bool:
    if locker["current_load"] >= locker["capacity"]:
        return False

    if order["size"] == "large" and not locker["accepts_large_packages"]:
        return False

    return True


def assign_round_robin_locker(
    order: Order,
    lockers: List[Locker],
    graph: Graph,
    start_index: int,
) -> Tuple[Assignment, int]:
    locker_count = len(lockers)

    for offset in range(locker_count):
        locker_index = (start_index + offset) % locker_count
        locker = lockers[locker_index]

        if not locker_can_accept_order(locker, order):
            continue

        distance_m, route = shortest_path(
            graph=graph,
            start=locker["location_node"],
            goal=order["destination"],
        )

        assignment = {
            "locker": locker,
            "distance_m": distance_m,
            "route": route,
            "score": distance_m,
        }

        next_start_index = (locker_index + 1) % locker_count
        return assignment, next_start_index

    raise ValueError("No eligible locker found for this order.")


def estimate_delivery_minutes(distance_m: float) -> float:
    return HANDOFF_TIME_MIN + (distance_m / DELIVERY_SPEED_M_PER_MIN)


def run_strategy(
    strategy_name: str,
    orders: List[Order],
    graph: Graph,
    base_lockers: List[Locker],
) -> Dict[str, float]:
    lockers = copy.deepcopy(base_lockers)

    distances: List[float] = []
    delivery_minutes: List[float] = []

    sla_successes = 0
    express_successes = 0
    express_total = 0
    failed_assignments = 0
    round_robin_index = 0

    for order in orders:
        if order["priority"] == "express":
            express_total += 1

        try:
            if strategy_name == "naive":
                assignment, round_robin_index = assign_round_robin_locker(
                    order=order,
                    lockers=lockers,
                    graph=graph,
                    start_index=round_robin_index,
                )
            elif strategy_name == "optimized":
                assignment = assign_best_locker(
                    order=order,
                    lockers=lockers,
                    graph=graph,
                )
            else:
                raise ValueError(f"Unknown strategy: {strategy_name}")

            assignment["locker"]["current_load"] += 1

            distance_m = assignment["distance_m"]
            estimated_minutes = estimate_delivery_minutes(distance_m)

            distances.append(distance_m)
            delivery_minutes.append(estimated_minutes)

            if estimated_minutes <= order["deadline_minutes"]:
                sla_successes += 1

                if order["priority"] == "express":
                    express_successes += 1

        except ValueError:
            failed_assignments += 1

    assigned_count = len(distances)

    return {
        "assigned_count": assigned_count,
        "failed_assignments": failed_assignments,
        "average_distance_m": round(mean(distances), 2) if distances else 0,
        "average_delivery_minutes": round(mean(delivery_minutes), 2) if delivery_minutes else 0,
        "sla_success_rate": round((sla_successes / len(orders)) * 100, 2) if orders else 0,
        "express_sla_success_rate": round((express_successes / express_total) * 100, 2)
        if express_total
        else 0,
    }


def percent_improvement(old_value: float, new_value: float) -> float:
    if old_value == 0:
        return 0

    return round(((old_value - new_value) / old_value) * 100, 2)


def get_fulfillment_metrics(
    order_count: int = DEFAULT_ORDER_COUNT,
    seed: int = DEFAULT_RANDOM_SEED,
) -> Dict[str, Any]:
    graph = build_campus_graph()
    lockers = build_lockers()

    raw_orders = generate_orders(order_count, seed)
    scheduled_orders = schedule_orders(raw_orders)

    naive_metrics = run_strategy(
        strategy_name="naive",
        orders=scheduled_orders,
        graph=graph,
        base_lockers=lockers,
    )

    optimized_metrics = run_strategy(
        strategy_name="optimized",
        orders=scheduled_orders,
        graph=graph,
        base_lockers=lockers,
    )

    return {
        "orders_simulated": order_count,
        "random_seed": seed,
        "scheduling": "heap-based express/deadline priority queue",
        "naive_strategy": naive_metrics,
        "optimized_strategy": optimized_metrics,
        "improvements": {
            "average_distance_reduced_percent": percent_improvement(
                naive_metrics["average_distance_m"],
                optimized_metrics["average_distance_m"],
            ),
            "average_delivery_time_reduced_percent": percent_improvement(
                naive_metrics["average_delivery_minutes"],
                optimized_metrics["average_delivery_minutes"],
            ),
            "overall_sla_gain_percentage_points": round(
                optimized_metrics["sla_success_rate"] - naive_metrics["sla_success_rate"],
                2,
            ),
            "express_sla_gain_percentage_points": round(
                optimized_metrics["express_sla_success_rate"]
                - naive_metrics["express_sla_success_rate"],
                2,
            ),
        },
    }
