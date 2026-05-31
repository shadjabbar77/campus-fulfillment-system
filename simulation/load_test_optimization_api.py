import json
import random
import statistics
import time
from typing import Dict, List
from urllib import request, error


API_URL = "http://127.0.0.1:8010/optimization/orders"
REQUEST_COUNT = 200
RANDOM_SEED = 42


def generate_order(order_id: int) -> Dict:
    destinations = [
        "Brock Commons",
        "Koerner Library",
        "Buchanan",
        "Sauder",
        "Place Vanier",
        "Totem Park",
        "Exchange Residence",
        "Thunderbird Residence",
        "Engineering",
        "Bookstore",
    ]

    priority = random.choices(["express", "standard"], weights=[0.25, 0.75], k=1)[0]
    size = random.choices(["small", "medium", "large"], weights=[0.50, 0.40, 0.10], k=1)[0]

    deadline_minutes = random.randint(12, 30) if priority == "express" else random.randint(45, 120)

    return {
        "id": order_id,
        "destination": random.choice(destinations),
        "priority": priority,
        "size": size,
        "deadline_minutes": deadline_minutes,
    }


def post_order(order: Dict) -> float:
    payload = json.dumps(order).encode("utf-8")

    req = request.Request(
        API_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    start = time.perf_counter()

    with request.urlopen(req, timeout=5) as response:
        response.read()

        if response.status != 200:
            raise RuntimeError(f"Unexpected status code: {response.status}")

    end = time.perf_counter()

    return (end - start) * 1000


def main() -> None:
    random.seed(RANDOM_SEED)

    latencies_ms: List[float] = []
    failures = 0

    print("CampusFlow API Load Test")
    print("========================")
    print(f"Endpoint:       {API_URL}")
    print(f"Requests:       {REQUEST_COUNT}")
    print(f"Random seed:    {RANDOM_SEED}")
    print()

    total_start = time.perf_counter()

    for order_id in range(1, REQUEST_COUNT + 1):
        order = generate_order(order_id)

        try:
            latency_ms = post_order(order)
            latencies_ms.append(latency_ms)
        except (error.URLError, TimeoutError, RuntimeError) as exc:
            failures += 1
            print(f"Request {order_id} failed: {exc}")

    total_end = time.perf_counter()
    total_seconds = total_end - total_start

    success_count = len(latencies_ms)
    success_rate = (success_count / REQUEST_COUNT) * 100
    requests_per_second = success_count / total_seconds if total_seconds > 0 else 0

    print()
    print("Results")
    print("-------")
    print(f"Successful requests:    {success_count}")
    print(f"Failed requests:        {failures}")
    print(f"Success rate:           {success_rate:.2f}%")
    print(f"Total time:             {total_seconds:.2f} sec")
    print(f"Throughput:             {requests_per_second:.2f} req/sec")

    if latencies_ms:
        print(f"Average latency:        {statistics.mean(latencies_ms):.2f} ms")
        print(f"Median latency:         {statistics.median(latencies_ms):.2f} ms")
        print(f"Fastest request:        {min(latencies_ms):.2f} ms")
        print(f"Slowest request:        {max(latencies_ms):.2f} ms")


if __name__ == "__main__":
    main()
