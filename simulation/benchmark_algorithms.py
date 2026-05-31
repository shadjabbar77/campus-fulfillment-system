import copy
import random
from statistics import mean
from typing import Any, Dict, List, Tuple

from app.services.locker_assignment import assign_best_locker
from app.services.pathfinding import Graph, shortest_path
from app.services.priority_scheduler import OrderPriorityScheduler


Locker = Dict[str, Any]
Order = Dict[str, Any]
Assignment = Dict[str, Any]

DELIVERY_SPEED_M_PER_MIN = 80
HANDOFF_TIME_MIN = 4
ORDER_COUNT = 1000
RANDOM_SEED = 42


def add_undirected_edge(graph: Graph, node_a: str, node_b: str, distance_m: int) -> None:
    graph[node_a][node_b] = distance_m
    graph[node_b][node_a] = distance_m


def build_campus_graph() -> Graph:
    """
    Simulated weighted campus graph.

    Nodes are campus locations.
    Edges are approximate walking distances in meters.
    """
    nodes = [
        "Campus Depot",
        "Nest",
        "IKB",
        "Koerner Library",
        "Brock Commons",
        "Life Building",
        "Buchanan",
        "Sauder",
        "Place Vanier",
        "Totem Park",
        "Exchange Residence",
        "Thunderbird Residence",
        "Engineering",
        "Bookstore",
    ]

    graph: Graph = {node: {} for node in nodes}

    add_undirected_edge(graph, "Campus Depot", "Nest", 250)
    add_undirected_edge(graph, "Nest", "IKB", 180)
    add_undirected_edge(graph, "IKB", "Koerner Library", 140)
    add_undirected_edge(graph, "IKB", "Brock Commons", 500)
    add_undirected_edge(graph, "Nest", "Life Building", 220)
    add_undirected_edge(graph, "Life Building", "Buchanan", 300)
    add_undirected_edge(graph, "Buchanan", "Koerner Library", 260)
    add_undirected_edge(graph, "Buchanan", "Sauder", 180)
    add_undirected_edge(graph, "Sauder", "Place Vanier", 500)
    add_undirected_edge(graph, "Place Vanier", "Totem Park", 450)
    add_undirected_edge(graph, "Brock Commons", "Exchange Residence", 300)
    add_undirected_edge(graph, "Exchange Residence", "Thunderbird Residence", 650)
    add_undirected_edge(graph, "Life Building", "Engineering", 350)
    add_undirected_edge(graph, "Engineering", "Thunderbird Residence", 700)
    add_undirected_edge(graph, "Nest", "Sauder", 350)
    add_undirected_edge(graph, "Nest", "Bookstore", 160)
    add_undirected_edge(graph, "Bookstore", "Koerner Library", 220)

    return graph


def build_lockers() -> List[Locker]:
    """
    Simulated locker network.

    Some lockers accept large packages.
    Some do not.
    """
    return [
        {
            "id": 1,
            "name": "Depot Overflow Locker",
            "location_node": "Campus Depot",
            "capacity": 1000,
            "current_load": 0,
            "accepts_large_packages": True,
        },
        {
            "id": 2,
            "name": "Nest Locker Bank",
            "location_node": "Nest",
            "capacity": 260,
            "current_load": 0,
            "accepts_large_packages": True,
        },
        {
            "id": 3,
            "name": "Brock Commons Lockers",
            "location_node": "Brock Commons",
            "capacity": 220,
            "current_load": 0,
            "accepts_large_packages": False,
        },
        {
            "id": 4,
            "name": "Koerner Library Lockers",
            "location_node": "Koerner Library",
            "capacity": 220,
            "current_load": 0,
            "accepts_large_packages": False,
        },
        {
            "id": 5,
            "name": "Totem Park Lockers",
            "location_node": "Totem Park",
            "capacity": 220,
            "current_load": 0,
            "accepts_large_packages": True,
        },
        {
            "id": 6,
            "name": "Thunderbird Lockers",
            "location_node": "Thunderbird Residence",
            "capacity": 220,
            "current_load": 0,
            "accepts_large_packages": True,
        },
        {
            "id": 7,
            "name": "Sauder Lockers",
            "location_node": "Sauder",
            "capacity": 220,
            "current_load": 0,
            "accepts_large_packages": False,
        },
    ]


def generate_orders(count: int, seed: int = RANDOM_SEED) -> List[Order]:
    """
    Generate deterministic simulated package orders.

    Express orders have tighter deadlines.
    Standard orders have more flexible deadlines.
    """
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
    """
    Process orders through the heap-based priority scheduler.

    This means express orders and earlier deadlines are handled first.
    """
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
    """
    Naive baseline strategy.

    It assigns the order to the next eligible locker in round-robin order.
    It ignores distance, deadline pressure, and route quality.
    """
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
        "average_distance_m": mean(distances) if distances else 0,
        "average_delivery_minutes": mean(delivery_minutes) if delivery_minutes else 0,
        "sla_success_rate": (sla_successes / len(orders)) * 100 if orders else 0,
        "express_sla_success_rate": (
            (express_successes / express_total) * 100 if express_total else 0
        ),
    }


def percent_improvement(old_value: float, new_value: float) -> float:
    if old_value == 0:
        return 0

    return ((old_value - new_value) / old_value) * 100


def print_metrics(label: str, metrics: Dict[str, float]) -> None:
    print(f"{label}")
    print("-" * len(label))
    print(f"Assigned packages:          {int(metrics['assigned_count'])}")
    print(f"Failed assignments:         {int(metrics['failed_assignments'])}")
    print(f"Average distance:           {metrics['average_distance_m']:.2f} m")
    print(f"Average delivery estimate:  {metrics['average_delivery_minutes']:.2f} min")
    print(f"Overall SLA success rate:   {metrics['sla_success_rate']:.2f}%")
    print(f"Express SLA success rate:   {metrics['express_sla_success_rate']:.2f}%")
    print()


def main() -> None:
    graph = build_campus_graph()
    lockers = build_lockers()

    raw_orders = generate_orders(ORDER_COUNT)
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

    distance_improvement = percent_improvement(
        naive_metrics["average_distance_m"],
        optimized_metrics["average_distance_m"],
    )

    delivery_time_improvement = percent_improvement(
        naive_metrics["average_delivery_minutes"],
        optimized_metrics["average_delivery_minutes"],
    )

    sla_gain = optimized_metrics["sla_success_rate"] - naive_metrics["sla_success_rate"]
    express_sla_gain = (
        optimized_metrics["express_sla_success_rate"]
        - naive_metrics["express_sla_success_rate"]
    )

    print()
    print("CampusFlow Algorithm Benchmark")
    print("==============================")
    print(f"Orders simulated:            {ORDER_COUNT}")
    print(f"Random seed:                 {RANDOM_SEED}")
    print("Scheduling:                  heap-based express/deadline priority queue")
    print("Naive baseline:              round-robin locker assignment")
    print("Optimized strategy:          capacity-aware shortest-path locker assignment")
    print()

    print_metrics("Naive strategy", naive_metrics)
    print_metrics("Optimized strategy", optimized_metrics)

    print("Improvement Summary")
    print("-------------------")
    print(f"Average distance reduced by:          {distance_improvement:.2f}%")
    print(f"Average delivery estimate reduced by: {delivery_time_improvement:.2f}%")
    print(f"Overall SLA success gain:             {sla_gain:.2f} percentage points")
    print(f"Express SLA success gain:             {express_sla_gain:.2f} percentage points")
    print()


if __name__ == "__main__":
    main()
