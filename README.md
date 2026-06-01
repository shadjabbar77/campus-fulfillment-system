# CampusFlow — Campus Package Fulfillment & Optimization System

![Backend Tests](https://github.com/shadjabbar77/campus-fulfillment-system/actions/workflows/tests.yml/badge.svg)

CampusFlow is a production-style FastAPI backend that simulates campus package pickup, locker fulfillment, order tracking, asynchronous fulfillment processing, and logistics optimization through one merged dashboard.

The system models a real campus package workflow where students create pickup requests, express orders are prioritized, lockers are assigned automatically, fulfillment jobs run through a Redis/RQ worker queue, and order data can be stored with PostgreSQL through Docker Compose.

CampusFlow also includes an optimization layer with Dijkstra shortest-path routing, capacity-aware locker assignment, heap-based priority scheduling, SLA delivery-time estimation, benchmark reporting, and API load testing.

---

## Project Highlights

* Built a FastAPI backend for package pickup requests, locker assignment, order tracking, dashboard views, and JSON API workflows.
* Implemented Dijkstra shortest-path routing to estimate efficient campus delivery paths.
* Added capacity-aware locker assignment for package size, locker capacity, and destination constraints.
* Implemented heap-based express priority scheduling so `EXPRESS` orders are processed before `STANDARD` orders.
* Integrated Redis/RQ background workers for asynchronous fulfillment and optimization jobs.
* Added SLA delivery-time estimation for fulfillment timing analysis.
* Added PostgreSQL persistence with Docker Compose.
* Created benchmark reporting for naive vs. optimized fulfillment behavior.
* Added API load testing for backend performance checks.
* Added automated Pytest coverage and GitHub Actions CI.
* Merged the order creation and optimization workflows into one dashboard so each package request can include destination, package size, deadline, optimized locker assignment, and queue processing in a single flow.

---

## Features

* Create campus package pickup requests.
* Track orders through `PENDING`, `READY_FOR_PICKUP`, `WAITING_FOR_LOCKER`, and `PICKED_UP`.
* Prioritize `EXPRESS` orders before `STANDARD` orders.
* Assign lockers automatically.
* Free lockers when packages are picked up.
* Process fulfillment jobs through a Redis-backed background queue.
* Store order data in PostgreSQL when running with Docker Compose.
* Estimate campus delivery paths using Dijkstra shortest-path routing.
* Support capacity-aware locker assignment.
* Estimate SLA delivery timing.
* Run synchronous optimization through the API.
* Run asynchronous optimization through Redis/RQ worker jobs.
* Generate benchmark reports.
* Run API load tests.
* Display order statistics on a dashboard.
* Provide JSON API endpoints for orders, stats, and optimization.
* Run automated tests with Pytest.
* Run CI checks with GitHub Actions.
* Start the full system with Docker Compose.
* Create optimized package pickup requests from one dashboard.
* Select delivery location, package size, priority, and deadline during order creation.
* Preserve optimized locker assignments during queue processing.

---

## Architecture

```txt
Dashboard / API Client
        |
        v
FastAPI Web App
        |
        | creates package orders
        v
PostgreSQL Database


FastAPI Web App
        |
        | enqueues fulfillment or optimization job
        v
Redis Queue
        |
        v
RQ Worker
        |
        | runs fulfillment / optimization logic
        v
PostgreSQL Database


Optimization Layer
        |
        | Dijkstra routing
        | capacity-aware locker assignment
        | priority scheduling
        | SLA estimation
        v
Fulfillment Decision Logic
```

---

## Optimization Engine

CampusFlow includes a backend optimization engine that can assign package orders to lockers and estimate route timing.

### Core Optimization Logic

| Feature                | Technique                      |
| ---------------------- | ------------------------------ |
| Route planning         | Dijkstra shortest-path search  |
| Express order handling | Heap-based priority queue      |
| Locker selection       | Capacity-aware scoring         |
| SLA tracking           | Delivery-time estimation       |
| Benchmarking           | Naive vs. optimized simulation |
| Async processing       | Redis/RQ worker jobs           |

### Example Optimization Request

```json
{
  "id": 99,
  "destination": "Thunderbird Residence",
  "priority": "express",
  "size": "large",
  "deadline_minutes": 30
}
```

### Example Optimization Response

```json
{
  "order_id": 99,
  "status": "assigned",
  "destination": "Thunderbird Residence",
  "priority": "express",
  "size": "large",
  "assigned_locker_name": "Thunderbird Lockers",
  "route": ["Thunderbird Residence"],
  "distance_m": 0.0,
  "estimated_delivery_minutes": 4.0,
  "sla_status": "on_time"
}
```

---

## Technologies

Python, FastAPI, PostgreSQL, Redis, RQ, SQLAlchemy, Jinja2, Uvicorn, Docker Compose, Pytest, GitHub Actions, REST APIs, HTML

---

## API Endpoints

### Main App

```txt
GET /
POST /orders
POST /process
POST /pickup/{order_id}
GET /optimizer
POST /optimizer
GET /api/orders
GET /api/stats
GET /docs
```

### Optimization API

```txt
GET  /optimization/health
GET  /optimization/campus
POST /optimization/orders
POST /optimization/jobs
GET  /optimization/jobs/{job_id}
```

---

## How to Run Locally

cd ~/campus-fulfillment-system
python3 -m uvicorn app.main:app --reload

Install dependencies:

```bash
pip install -r requirements.txt
```


Open the dashboard:

The main dashboard combines order creation, delivery-location selection, package-size selection, deadline input, optimized locker assignment, order tracking, and queue processing in one page.

```txt
http://127.0.0.1:8000
```

Open API docs:

```txt
http://127.0.0.1:8000/docs
```

---

## Running the Optimization API

Start the server:

```bash
cd backend
PYTHONPATH=. python3 -m uvicorn app.main:app --reload
```

Test the optimization health endpoint:

```bash
curl -s http://127.0.0.1:8000/optimization/health | python3 -m json.tool
```

Run a synchronous optimization request:

```bash
curl -s -X POST http://127.0.0.1:8000/optimization/orders \
  -H "Content-Type: application/json" \
  -d '{"id":99,"destination":"Thunderbird Residence","priority":"express","size":"large","deadline_minutes":30}' \
  | python3 -m json.tool
```

---

## Running Asynchronous Optimization Jobs

Start Redis:

```bash
docker compose up -d redis
```

Start the RQ worker in a separate terminal:

```bash
cd backend
PYTHONPATH=. rq worker fulfillment --url redis://localhost:6379/0
```

Start the FastAPI app in another terminal:

```bash
cd backend
PYTHONPATH=. python3 -m uvicorn app.main:app --reload
```

Enqueue an optimization job:

```bash
curl -s -X POST http://127.0.0.1:8000/optimization/jobs \
  -H "Content-Type: application/json" \
  -d '{"id":99,"destination":"Thunderbird Residence","priority":"express","size":"large","deadline_minutes":30}' \
  | python3 -m json.tool
```

Check a job result:

```bash
curl -s http://127.0.0.1:8000/optimization/jobs/YOUR_JOB_ID_HERE \
  | python3 -m json.tool
```

---

## How to Run with Docker Compose

Start the full system:

```bash
docker compose up --build
```

This starts:

```txt
web       FastAPI app
worker    RQ background worker
redis     Redis queue
db        PostgreSQL database
```

Open the dashboard:

```txt
http://127.0.0.1:8000
```

Open API docs:

```txt
http://127.0.0.1:8000/docs
```

Stop the system:

```bash
docker compose down
```

---

## Testing

Run the full test suite:

```bash
pytest -q
```

Run the algorithm and optimization tests from the backend folder:

```bash
cd backend
PYTHONPATH=. python3 -m pytest app/tests
```

The project also includes GitHub Actions CI to automatically run backend tests on GitHub.

---

## Benchmarking and Load Testing

Run the optimization benchmark script:

```bash
PYTHONPATH=backend python3 simulation/benchmark_algorithms.py
```

Generate the benchmark report:

```bash
PYTHONPATH=backend python3 simulation/generate_benchmark_report.py
```

Run the API load test script:

```bash
python3 simulation/load_test_optimization_api.py
```

Benchmark reports are stored in:

```txt
docs/benchmark.md
```

---

## Resume Relevance

CampusFlow demonstrates backend engineering skills including API design, database persistence, asynchronous job processing, queue-based workflows, Redis/RQ workers, shortest-path routing, priority scheduling, SLA estimation, performance benchmarking, Dockerized services, automated testing, and CI/CD with GitHub Actions.

This project is designed to show both application-building ability and computer science fundamentals through routing algorithms, priority queues, optimization logic, and production-style backend architecture.

---

## Privacy Note

Local database files, Docker volumes, and demo order data are excluded from GitHub because they may contain test names, emails, package codes, and order history.
