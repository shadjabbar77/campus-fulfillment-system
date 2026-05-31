import pytest

from app.services.locker_assignment import assign_best_locker


def test_assign_best_locker_chooses_nearest_available_locker():
    graph = {
        "Near Locker": {"Destination": 100},
        "Far Locker": {"Destination": 500},
        "Destination": {},
    }

    order = {
        "destination": "Destination",
        "priority": "standard",
        "size": "medium",
    }

    lockers = [
        {
            "id": 1,
            "name": "Far Locker",
            "location_node": "Far Locker",
            "capacity": 10,
            "current_load": 0,
            "accepts_large_packages": True,
        },
        {
            "id": 2,
            "name": "Near Locker",
            "location_node": "Near Locker",
            "capacity": 10,
            "current_load": 0,
            "accepts_large_packages": True,
        },
    ]

    assignment = assign_best_locker(order, lockers, graph)

    assert assignment["locker"]["name"] == "Near Locker"
    assert assignment["distance_m"] == 100
    assert assignment["route"] == ["Near Locker", "Destination"]


def test_assign_best_locker_skips_full_lockers():
    graph = {
        "Full Near Locker": {"Destination": 100},
        "Open Far Locker": {"Destination": 400},
        "Destination": {},
    }

    order = {
        "destination": "Destination",
        "priority": "standard",
        "size": "medium",
    }

    lockers = [
        {
            "id": 1,
            "name": "Full Near Locker",
            "location_node": "Full Near Locker",
            "capacity": 5,
            "current_load": 5,
            "accepts_large_packages": True,
        },
        {
            "id": 2,
            "name": "Open Far Locker",
            "location_node": "Open Far Locker",
            "capacity": 10,
            "current_load": 2,
            "accepts_large_packages": True,
        },
    ]

    assignment = assign_best_locker(order, lockers, graph)

    assert assignment["locker"]["name"] == "Open Far Locker"
    assert assignment["distance_m"] == 400


def test_assign_best_locker_rejects_large_package_when_locker_cannot_accept_large():
    graph = {
        "Small Locker": {"Destination": 100},
        "Large Locker": {"Destination": 300},
        "Destination": {},
    }

    order = {
        "destination": "Destination",
        "priority": "standard",
        "size": "large",
    }

    lockers = [
        {
            "id": 1,
            "name": "Small Locker",
            "location_node": "Small Locker",
            "capacity": 10,
            "current_load": 0,
            "accepts_large_packages": False,
        },
        {
            "id": 2,
            "name": "Large Locker",
            "location_node": "Large Locker",
            "capacity": 10,
            "current_load": 0,
            "accepts_large_packages": True,
        },
    ]

    assignment = assign_best_locker(order, lockers, graph)

    assert assignment["locker"]["name"] == "Large Locker"


def test_assign_best_locker_raises_error_when_no_locker_is_available():
    graph = {
        "Full Locker": {"Destination": 100},
        "Destination": {},
    }

    order = {
        "destination": "Destination",
        "priority": "standard",
        "size": "medium",
    }

    lockers = [
        {
            "id": 1,
            "name": "Full Locker",
            "location_node": "Full Locker",
            "capacity": 3,
            "current_load": 3,
            "accepts_large_packages": True,
        }
    ]

    with pytest.raises(ValueError):
        assign_best_locker(order, lockers, graph)
