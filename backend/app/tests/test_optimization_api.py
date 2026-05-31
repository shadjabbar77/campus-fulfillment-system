from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_optimization_health_endpoint():
    response = client.get("/optimization/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "campusflow-optimization",
    }


def test_campus_data_endpoint_returns_graph_summary_and_lockers():
    response = client.get("/optimization/campus")

    assert response.status_code == 200

    data = response.json()

    assert "nodes" in data
    assert "edge_count" in data
    assert "lockers" in data
    assert "Brock Commons" in data["nodes"]
    assert data["edge_count"] > 0
    assert len(data["lockers"]) > 0


def test_sync_optimization_endpoint_assigns_locker_and_route():
    payload = {
        "id": 42,
        "destination": "Brock Commons",
        "priority": "express",
        "size": "medium",
        "deadline_minutes": 25,
    }

    response = client.post("/optimization/orders", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert data["order_id"] == 42
    assert data["status"] == "assigned"
    assert data["destination"] == "Brock Commons"
    assert data["priority"] == "express"
    assert data["size"] == "medium"
    assert data["assigned_locker_name"] == "Brock Commons Lockers"
    assert data["route"] == ["Brock Commons"]
    assert data["sla_status"] == "on_time"


def test_sync_optimization_endpoint_rejects_unknown_destination():
    payload = {
        "id": 43,
        "destination": "Unknown Building",
        "priority": "express",
        "size": "medium",
        "deadline_minutes": 25,
    }

    response = client.post("/optimization/orders", json=payload)

    assert response.status_code == 400
    assert "does not exist in the campus graph" in response.json()["detail"]


def test_sync_optimization_endpoint_rejects_invalid_priority():
    payload = {
        "id": 44,
        "destination": "Nest",
        "priority": "urgent",
        "size": "medium",
        "deadline_minutes": 25,
    }

    response = client.post("/optimization/orders", json=payload)

    assert response.status_code == 400
    assert "Unsupported priority" in response.json()["detail"]


def test_metrics_endpoint_returns_benchmark_summary():
    response = client.get("/optimization/metrics")

    assert response.status_code == 200

    data = response.json()

    assert data["orders_simulated"] == 1000
    assert data["random_seed"] == 42
    assert "naive_strategy" in data
    assert "optimized_strategy" in data
    assert "improvements" in data
    assert "average_distance_reduced_percent" in data["improvements"]
    assert data["optimized_strategy"]["average_distance_m"] <= data["naive_strategy"]["average_distance_m"]
