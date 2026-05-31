from typing import Any, Dict, List

from app.services.pathfinding import Graph


Locker = Dict[str, Any]


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
