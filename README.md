# Campus Package Fulfillment System

A FastAPI-based backend project that simulates an Amazon-style package pickup and locker fulfillment system for a campus.

## Features

* Create package pickup requests
* Store orders in a SQLite database
* Track order statuses: `PENDING`, `READY_FOR_PICKUP`, `WAITING_FOR_LOCKER`, and `PICKED_UP`
* Process pending orders through a queue-style worker
* Automatically assign available locker numbers
* Free lockers when packages are picked up
* Display dashboard counts for each order status
* Provide backend API endpoints for orders and stats
* Includes automatic FastAPI documentation at `/docs`

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

The local SQLite database is excluded from GitHub because it may contain demo student names, emails, and order data.
