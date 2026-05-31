import pytest

from app.services.priority_scheduler import OrderPriorityScheduler


def test_scheduler_processes_express_before_standard():
    scheduler = OrderPriorityScheduler()

    standard_order = {
        "id": 1,
        "priority": "standard",
        "deadline_minutes": 10,
    }

    express_order = {
        "id": 2,
        "priority": "express",
        "deadline_minutes": 60,
    }

    scheduler.add_order(standard_order)
    scheduler.add_order(express_order)

    next_order = scheduler.pop_next_order()

    assert next_order["id"] == 2


def test_scheduler_processes_earliest_deadline_with_same_priority():
    scheduler = OrderPriorityScheduler()

    later_express_order = {
        "id": 1,
        "priority": "express",
        "deadline_minutes": 90,
    }

    earlier_express_order = {
        "id": 2,
        "priority": "express",
        "deadline_minutes": 30,
    }

    scheduler.add_order(later_express_order)
    scheduler.add_order(earlier_express_order)

    next_order = scheduler.pop_next_order()

    assert next_order["id"] == 2


def test_scheduler_preserves_fifo_when_priority_and_deadline_match():
    scheduler = OrderPriorityScheduler()

    first_order = {
        "id": 1,
        "priority": "standard",
        "deadline_minutes": 60,
    }

    second_order = {
        "id": 2,
        "priority": "standard",
        "deadline_minutes": 60,
    }

    scheduler.add_order(first_order)
    scheduler.add_order(second_order)

    assert scheduler.pop_next_order()["id"] == 1
    assert scheduler.pop_next_order()["id"] == 2


def test_scheduler_peek_does_not_remove_order():
    scheduler = OrderPriorityScheduler()

    order = {
        "id": 1,
        "priority": "express",
        "deadline_minutes": 20,
    }

    scheduler.add_order(order)

    peeked_order = scheduler.peek_next_order()

    assert peeked_order["id"] == 1
    assert scheduler.size() == 1


def test_scheduler_returns_none_when_empty():
    scheduler = OrderPriorityScheduler()

    assert scheduler.pop_next_order() is None
    assert scheduler.peek_next_order() is None
    assert scheduler.is_empty() is True


def test_scheduler_rejects_invalid_priority():
    scheduler = OrderPriorityScheduler()

    order = {
        "id": 1,
        "priority": "urgent",
        "deadline_minutes": 20,
    }

    with pytest.raises(ValueError):
        scheduler.add_order(order)


def test_scheduler_rejects_missing_deadline():
    scheduler = OrderPriorityScheduler()

    order = {
        "id": 1,
        "priority": "express",
    }

    with pytest.raises(ValueError):
        scheduler.add_order(order)
