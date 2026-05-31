import pytest

from app.services.pathfinding import shortest_path


def test_shortest_path_finds_best_route():
    graph = {
        "A": {"B": 5, "C": 2},
        "B": {"D": 2},
        "C": {"B": 1, "D": 10},
        "D": {}
    }

    distance, path = shortest_path(graph, "A", "D")

    assert distance == 5
    assert path == ["A", "C", "B", "D"]


def test_shortest_path_direct_route():
    graph = {
        "Nest": {"IKB": 180},
        "IKB": {}
    }

    distance, path = shortest_path(graph, "Nest", "IKB")

    assert distance == 180
    assert path == ["Nest", "IKB"]


def test_shortest_path_rejects_unknown_start():
    graph = {
        "Nest": {"IKB": 180},
        "IKB": {}
    }

    with pytest.raises(ValueError):
        shortest_path(graph, "Unknown", "IKB")


def test_shortest_path_rejects_unknown_goal():
    graph = {
        "Nest": {"IKB": 180},
        "IKB": {}
    }

    with pytest.raises(ValueError):
        shortest_path(graph, "Nest", "Unknown")