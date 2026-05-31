# CampusFlow Benchmark Report

CampusFlow is a campus logistics optimization simulation that compares a naive package fulfillment strategy against a capacity-aware shortest-path optimization strategy.

The benchmark is deterministic and generated from `simulation/benchmark_algorithms.py`.

## Simulation Setup

| Setting | Value |
|---|---:|
| Orders simulated | 1000 |
| Random seed | 42 |
| Scheduling strategy | Heap-based priority queue |
| Priority rules | Express orders first, then earliest deadline |
| Naive baseline | Round-robin locker assignment |
| Optimized strategy | Capacity-aware shortest-path locker assignment |

## Results

| Metric | Naive Strategy | Optimized Strategy | Improvement |
|---|---:|---:|---:|
| Assigned packages | 1000 | 1000 | — |
| Failed assignments | 0 | 0 | — |
| Average delivery distance | 975.25 m | 181.15 m | 81.43% lower |
| Average delivery estimate | 16.19 min | 6.26 min | 61.31% lower |
| Overall SLA success rate | 92.20% | 100.00% | +7.80 percentage points |
| Express SLA success rate | 66.67% | 100.00% | +33.33 percentage points |

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
