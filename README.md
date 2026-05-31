# Campus Package Fulfillment System

A FastAPI backend project that simulates an Amazon-style package pickup and locker fulfillment system for a campus.

![Backend Tests](https://github.com/shadjabbar77/campus-fulfillment-system/actions/workflows/tests.yml/badge.svg)

## Features

* Create package pickup requests
* Store package orders in a SQLite database
* Track order statuses: `PENDING`, `READY_FOR_PICKUP`, `WAITING_FOR_LOCKER`, and `PICKED_UP`
* Process orders using queue-style fulfillment logic
* Prioritize `EXPRESS` orders before `STANDARD` orders
* Automatically assign available locker numbers
* Free lockers when packages are picked up
* Display dashboard counts for order statuses and priorities
* Provide JSON API endpoints for orders and system stats
* Includes FastAPI automatic API documentation at `/docs`
* Uses Redis + RQ for background queue processing
* Runs with Docker Compose using separate web, worker, and Redis services
* Shares a database volume between the web app and background worker
* Includes automated pytest tests
* Uses GitHub Actions CI to run tests on every push

## Technologies

Python, FastAPI, SQLAlchemy, SQLite, Jinja2, Uvicorn, HTML, Git

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

## How to Run

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the server:

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

## Privacy Note

The local SQLite database is excluded from GitHub because it may contain demo student names, emails, package codes, and order history.
