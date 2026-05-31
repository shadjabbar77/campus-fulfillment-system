# CampusFlow — Campus Package Fulfillment & Optimization System

![Backend Tests](https://github.com/shadjabbar77/campus-fulfillment-system/actions/workflows/tests.yml/badge.svg)

A production-style FastAPI backend simulation for campus package pickup, locker fulfillment, order tracking, and fulfillment optimization.

CampusFlow models a real logistics workflow where students create pickup requests, express orders are prioritized, lockers are assigned automatically, fulfillment jobs run through a Redis-backed worker queue, and order data is stored with PostgreSQL when running through Docker Compose.

The project also includes optimization features such as shortest-path routing, capacity-aware locker assignment, SLA delivery-time estimation, benchmark reporting, and API load testing.

## Project Highlights

* Built a FastAPI backend for package pickup requests, locker assignment, order tracking, dashboard views, and JSON API workflows
* Implemented Dijkstra shortest-path routing to estimate efficient campus delivery paths
* Added capacity-aware locker assignment for package fulfillment constraints
* Implemented heap-based express priority scheduling so `EXPRESS` orders are processed before `STANDARD` orders
* Added SLA delivery-time estimation for fulfillment timing analysis
* Integrated Redis/RQ background workers for asynchronous fulfillment processing
* Added PostgreSQL persistence with Docker Compose
* Created benchmark reports for optimization logic
* Added API load testing for backend performance checks
* Created automated Pytest coverage and GitHub Actions CI

## Features

* Create package pickup requests
* Track orders through `PENDING`, `READY_FOR_PICKUP`, `WAITING_FOR_LOCKER`, and `PICKED_UP`
* Prioritize `EXPRESS` orders before `STANDARD` orders
* Assign available locker numbers automatically
* Free lockers when packages are picked up
* Process fulfillment jobs through a Redis-backed background queue
* Store order data in PostgreSQL when running with Docker Compose
* Estimate campus routing paths using Dijkstra shortest-path logic
* Support capacity-aware locker assignment
* Estimate SLA delivery timing
* Generate benchmark reports
* Run API load tests
* Display order statistics on a dashboard
* Provide JSON API endpoints for orders and stats
* Run automated tests with Pytest
* Run CI checks with GitHub Actions
* Start the full system with Docker Compose

## Architecture

```txt
User Dashboard / API Client
     |
     v
FastAPI Web App
     |
     | creates package orders
     v
PostgreSQL Database

FastAPI Web App
     |
     | sends fulfillment job
     v
Redis Queue
     |
     v
RQ Worker
     |
     | processes pending orders
     v
PostgreSQL Database

Optimization Layer
     |
     | routing, priority scheduling, SLA estimation
     v
Fulfillment Decision Logic
```

## Technologies

Python, FastAPI, PostgreSQL, Redis, RQ, SQLAlchemy, Jinja2, Uvicorn, Docker Compose, Pytest, GitHub Actions, REST APIs, HTML

## API Endpoints

```txt
GET  /
POST /orders
POST /process
POST /pickup/{order_id}
GET  /api/orders
GET  /api/stats
GET  /docs
```

## Optimization Features

* **Dijkstra shortest-path routing:** estimates efficient campus delivery routes between package locations and locker destinations
* **Heap-based priority scheduling:** processes express orders before standard orders using priority queue logic
* **Capacity-aware locker assignment:** assigns packages based on available locker capacity
* **SLA delivery-time estimation:** estimates fulfillment timing for delivery workflow analysis
* **Benchmark reports:** compares optimization behavior and runtime results
* **API load testing:** checks backend API performance under repeated requests

## How to Run Locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Run tests:

```bash
pytest -q
```

Start the local FastAPI server:

```bash
uvicorn app.main:app --reload
```

Open the dashboard:

```txt
http://127.0.0.1:8000
```

Open API docs:

```txt
http://127.0.0.1:8000/docs
```

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

## Testing

Run the test suite:

```bash
pytest -q
```

The project also includes GitHub Actions CI to automatically run backend tests on GitHub.

## Benchmarking and Load Testing

Run the optimization benchmark script:

```bash
PYTHONPATH=. python simulation/benchmark_algorithms.py
```

Run the API load test script:

```bash
python simulation/load_test_optimization_api.py
```

## Resume Relevance

This project demonstrates backend engineering skills including API design, database persistence, asynchronous job processing, queue-based workflows, shortest-path routing, priority scheduling, performance benchmarking, Dockerized services, automated testing, and CI/CD with GitHub Actions.

## Privacy Note

Local database files, Docker volumes, and demo order data are excluded from GitHub because they may contain test names, emails, package codes, and order history.
