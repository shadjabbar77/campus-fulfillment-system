from pathlib import Path
from typing import Dict

from benchmark_algorithms import (
    ORDER_COUNT,
    RANDOM_SEED,
    build_campus_graph,
    build_lockers,
    generate_orders,
    percent_improvement,
    run_strategy,
    schedule_orders,
)


def format_percent(value: float) -> str:
    return f"{value:.2f}%"


def format_points(value: float) -> str:
    return f"{value:.2f} percentage points"


def format_metric(value: float, suffix: str = "") -> str:
    return f"{value:.2f}{suffix}"


def build_report(
    naive_metrics: Dict[str, float],
    optimized_metrics: Dict[str, float],
) -> str:
    distance_improvement = percent_improvement(
        naive_metrics["average_distance_m"],
        optimized_metrics["average_distance_m"],
    )

    delivery_time_improvement = percent_improvement(
        naive_metrics["average_delivery_minutes"],
        optimized_metrics["average_delivery_minutes"],
    )

    sla_gain = (
        optimized_metrics["sla_success_rate"]
        - naive_metrics["sla_success_rate"]
    )

    express_sla_gain = (
        optimized_metrics["express_sla_success_rate"]
        - naive_metrics["express_sla_success_rate"]
    )

    return f"""# CampusFlow Benchmark Report

CampusFlow is a campus logistics optimization simulation that compares a naive package fulfillment strategy against a capacity-aware shortest-path optimization strategy.

The benchmark is deterministic and generated from `simulation/benchmark_algorithms.py`.

## Simulation Setup

| Setting | Value |
|---|---:|
| Orders simulated | {ORDER_COUNT} |
| Random seed | {RANDOM_SEED} |
| Scheduling strategy | Heap-based priority queue |
| Priority rules | Express orders first, then earliest deadline |
| Naive baseline | Round-robin locker assignment |
| Optimized strategy | Capacity-aware shortest-path locker assignment |

## Results

| Metric | Naive Strategy | Optimized Strategy | Improvement |
|---|---:|---:|---:|
| Assigned packages | {int(naive_metrics["assigned_count"])} | {int(optimized_metrics["assigned_count"])} | — |
| Failed assignments | {int(naive_metrics["failed_assignments"])} | {int(optimized_metrics["failed_assignments"])} | — |
| Average delivery distance | {format_metric(naive_metrics["average_distance_m"], " m")} | {format_metric(optimized_metrics["average_distance_m"], " m")} | {format_percent(distance_improvement)} lower |
| Average delivery estimate | {format_metric(naive_metrics["average_delivery_minutes"], " min")} | {format_metric(optimized_metrics["average_delivery_minutes"], " min")} | {format_percent(delivery_time_improvement)} lower |
| Overall SLA success rate | {format_percent(naive_metrics["sla_success_rate"])} | {format_percent(optimized_metrics["sla_success_rate"])} | +{format_points(sla_gain)} |
| Express SLA success rate | {format_percent(naive_metrics["express_sla_success_rate"])} | {format_percent(optimized_metrics["express_sla_success_rate"])} | +{format_points(express_sla_gain)} |

## Algorithms Used

### Dijkstra Shortest-Path Routing

Campus locations are represented as nodes in a weighted graph. Walking paths are represented as weighted edges. CampusFlow uses Dijkstra's algorithm to compute the shortest route between lockers and destinations.

### Capacity-Aware Locker Assignment

The optimized strategy assigns packages to lockers using a score based on:

- Walking distance to destination
- Locker capacity utilization
- Package size constraints
- Express-priority handling

### Heap-Based Priority Scheduling

Orders are processed through a heap-based priority queue. Express orders are handled before standard orders, and orders with earlier deadlines are processed first within the same priority class.

## Interpretation

The optimized strategy reduces simulated delivery distance by selecting lockers closer to each package destination while respecting locker capacity and package-size constraints.

These are simulated benchmark results, not real-world operational measurements.
"""


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

    report = build_report(naive_metrics, optimized_metrics)

    output_path = Path("docs/benchmark.md")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report)

    print(f"Generated {output_path}")


if __name__ == "__main__":
    main()
