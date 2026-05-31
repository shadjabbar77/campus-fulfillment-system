import pytest

from app.services.optimization_engine import optimize_order


def test_optimize_order_assigns_best_locker_and_route():
    order = {
        "id": 42,
        "destination": "Brock Commons",
        "priority": "express",
        "size": "medium",
        "deadline_minutes": 25,
    }

    result = optimize_order(order)

    assert result["order_id"] == 42
    assert result["status"] == "assigned"
    assert result["destination"] == "Brock Commons"
    assert result["priority"] == "express"
    assert result["assigned_locker_name"] == "Brock Commons Lockers"
    assert result["route"] == ["Brock Commons"]
    assert result["distance_m"] == 0
    assert result["estimated_delivery_minutes"] == 4
    assert result["sla_status"] == "on_time"


def test_optimize_order_routes_large_package_to_large_eligible_locker():
    order = {
        "id": 100,
        "destination": "Brock Commons",
        "priority": "standard",
        "size": "large",
        "deadline_minutes": 90,
    }

    result = optimize_order(order)

    assert result["assigned_locker_name"] != "Brock Commons Lockers"
    assert result["size"] == "large"


def test_optimize_order_marks_late_delivery_when_deadline_is_too_tight():
    order = {
        "id": 7,
        "destination": "Thunderbird Residence",
        "priority": "express",
        "size": "medium",
        "deadline_minutes": 1,
    }

    result = optimize_order(order)

    assert result["sla_status"] == "late"


def test_optimize_order_rejects_unknown_destination():
    order = {
        "id": 8,
        "destination": "Unknown Building",
        "priority": "express",
        "size": "medium",
        "deadline_minutes": 30,
    }

    with pytest.raises(ValueError):
        optimize_order(order)


def test_optimize_order_rejects_invalid_priority():
    order = {
        "id": 9,
        "destination": "Nest",
        "priority": "urgent",
        "size": "medium",
        "deadline_minutes": 30,
    }

    with pytest.raises(ValueError):
        optimize_order(order)


def test_optimize_order_rejects_invalid_package_size():
    order = {
        "id": 10,
        "destination": "Nest",
        "priority": "express",
        "size": "gigantic",
        "deadline_minutes": 30,
    }

    with pytest.raises(ValueError):
        optimize_order(order)
