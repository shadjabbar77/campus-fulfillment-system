import heapq
from itertools import count
from typing import Any, Dict, List, Optional, Tuple


Order = Dict[str, Any]


class OrderPriorityScheduler:
    """
    Heap-based scheduler for processing campus package orders.

    Ordering rules:
    1. Express orders before standard orders.
    2. Earlier deadlines before later deadlines.
    3. FIFO ordering when priority and deadline are tied.
    """

    def __init__(self) -> None:
        self._queue: List[Tuple[int, int, int, Order]] = []
        self._counter = count()

    def add_order(self, order: Order) -> None:
        if "priority" not in order:
            raise ValueError("Order must include a priority.")

        if "deadline_minutes" not in order:
            raise ValueError("Order must include deadline_minutes.")

        priority_rank = self._priority_rank(order["priority"])
        deadline_minutes = int(order["deadline_minutes"])
        insertion_order = next(self._counter)

        heapq.heappush(
            self._queue,
            (priority_rank, deadline_minutes, insertion_order, order)
        )

    def pop_next_order(self) -> Optional[Order]:
        if not self._queue:
            return None

        return heapq.heappop(self._queue)[-1]

    def peek_next_order(self) -> Optional[Order]:
        if not self._queue:
            return None

        return self._queue[0][-1]

    def size(self) -> int:
        return len(self._queue)

    def is_empty(self) -> bool:
        return len(self._queue) == 0

    @staticmethod
    def _priority_rank(priority: str) -> int:
        normalized_priority = priority.lower().strip()

        if normalized_priority == "express":
            return 0

        if normalized_priority == "standard":
            return 1

        raise ValueError(f"Unsupported priority: {priority}")
