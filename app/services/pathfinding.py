import heapq
from typing import Dict, List, Tuple


Graph = Dict[str, Dict[str, int]]


def shortest_path(graph: Graph, start: str, goal: str) -> Tuple[int, List[str]]:
    """
    Find the shortest path between two campus locations using Dijkstra's algorithm.

    Args:
        graph: Weighted adjacency list.
        start: Starting campus node.
        goal: Destination campus node.

    Returns:
        A tuple containing total distance and the path taken.
    """
    if start not in graph:
        raise ValueError(f"Start node '{start}' does not exist in the graph.")

    if goal not in graph:
        raise ValueError(f"Goal node '{goal}' does not exist in the graph.")

    queue = [(0, start, [])]
    visited = set()

    while queue:
        distance, node, path = heapq.heappop(queue)

        if node in visited:
            continue

        visited.add(node)
        path = path + [node]

        if node == goal:
            return distance, path

        for neighbor, weight in graph[node].items():
            if neighbor not in visited:
                heapq.heappush(queue, (distance + weight, neighbor, path))

    raise ValueError(f"No path found from '{start}' to '{goal}'.")