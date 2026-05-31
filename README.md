# Campus Package Fulfillment System

![Backend Tests](https://github.com/shadjabbar77/campus-fulfillment-system/actions/workflows/tests.yml/badge.svg)

A production-style FastAPI backend project that simulates a logistics fulfillment system for campus package pickup and locker assignment.

The system supports package pickup requests, express-priority queue processing, locker assignment, order status tracking, a dashboard, JSON API endpoints, Docker Compose services, Redis-backed background jobs, PostgreSQL persistence, automated tests, and GitHub Actions CI.


## Features

* Create package pickup requests
* Track orders through `PENDING`, `READY_FOR_PICKUP`, `WAITING_FOR_LOCKER`, and `PICKED_UP`
* Prioritize `EXPRESS` orders before `STANDARD` orders
* Assign available locker numbers automatically
* Free lockers when packages are picked up
* Process fulfillment jobs through a Redis-backed background queue
* Store order data in PostgreSQL when running with Docker Compose
* Display order statistics on a dashboard
* Provide JSON API endpoints for orders and stats
* Include automated pytest tests
* Run tests automatically with GitHub Actions CI
* Run the full system with Docker Compose

## Architecture

```txt
User Dashboard
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
```

## Technologies

Python, FastAPI, PostgreSQL, Redis, RQ, SQLAlchemy, Jinja2, Uvicorn, Docker Compose, Pytest, GitHub Actions, HTML, Git

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

Open:

```txt
http://127.0.0.1:8000
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

## Privacy Note

Local database files, Docker volumes, and demo order data are excluded from GitHub because they may contain test names, emails, package codes, and order history.
