import os
import uuid

from fastapi import Depends, FastAPI, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from redis import Redis
from redis.exceptions import RedisError
from rq import Queue
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import PackageOrder
from app.queue_worker import process_all_pending_orders
from app.worker import process_queue_job

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Campus Package Fulfillment System")

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_conn = Redis.from_url(REDIS_URL)
task_queue = Queue("fulfillment", connection=redis_conn)


@app.get("/")
def dashboard(request: Request, db: Session = Depends(get_db)):
    from app.services.campus_data import build_campus_graph

    orders = db.query(PackageOrder).order_by(PackageOrder.created_at.desc()).all()
    graph = build_campus_graph()

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "orders": orders,
            "destinations": sorted(graph.keys()),
            "optimizer_result": None,
            "optimizer_error": None,
            "pending_count": db.query(PackageOrder).filter(PackageOrder.status == "PENDING").count(),
            "ready_count": db.query(PackageOrder).filter(PackageOrder.status == "READY_FOR_PICKUP").count(),
            "waiting_count": db.query(PackageOrder).filter(PackageOrder.status == "WAITING_FOR_LOCKER").count(),
            "picked_up_count": db.query(PackageOrder).filter(PackageOrder.status == "PICKED_UP").count(),
            "express_count": db.query(PackageOrder).filter(PackageOrder.priority == "EXPRESS").count(),
            "standard_count": db.query(PackageOrder).filter(PackageOrder.priority == "STANDARD").count(),
        },
    )


@app.post("/orders")
def create_order(
    student_name: str = Form(...),
    student_email: str = Form(...),
    priority: str = Form("STANDARD"),
    destination: str = Form("Brock Commons"),
    size: str = Form("medium"),
    deadline_minutes: int = Form(30),
    db: Session = Depends(get_db),
):
    from app.services.optimization_engine import optimize_order

    priority = priority.upper()

    if priority not in ["STANDARD", "EXPRESS"]:
        priority = "STANDARD"

    package_code = f"PKG-{uuid.uuid4().hex[:8].upper()}"

    optimizer_payload = {
        "id": 1,
        "destination": destination,
        "priority": priority.lower(),
        "size": size,
        "deadline_minutes": deadline_minutes,
    }

    try:
        optimizer_result = optimize_order(optimizer_payload)
        locker_number = optimizer_result.get("assigned_locker_name")
    except ValueError:
        locker_number = None

    order = PackageOrder(
        student_name=student_name,
        student_email=student_email,
        package_code=package_code,
        priority=priority,
        status="PENDING",
        locker_number=locker_number,
    )

    db.add(order)
    db.commit()

    return RedirectResponse("/", status_code=303)

@app.post("/orders/optimize")
def optimize_from_orders_page(
    request: Request,
    destination: str = Form(...),
    priority: str = Form("express"),
    size: str = Form("medium"),
    deadline_minutes: int = Form(30),
    db: Session = Depends(get_db),
):
    from app.services.campus_data import build_campus_graph
    from app.services.optimization_engine import optimize_order

    orders = db.query(PackageOrder).order_by(PackageOrder.created_at.desc()).all()
    graph = build_campus_graph()

    order = {
        "id": 1,
        "destination": destination,
        "priority": priority,
        "size": size,
        "deadline_minutes": deadline_minutes,
    }

    try:
        optimizer_result = optimize_order(order)
        optimizer_error = None
    except ValueError as exc:
        optimizer_result = None
        optimizer_error = str(exc)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "orders": orders,
            "destinations": sorted(graph.keys()),
            "optimizer_result": optimizer_result,
            "optimizer_error": optimizer_error,
            "pending_count": db.query(PackageOrder).filter(PackageOrder.status == "PENDING").count(),
            "ready_count": db.query(PackageOrder).filter(PackageOrder.status == "READY_FOR_PICKUP").count(),
            "waiting_count": db.query(PackageOrder).filter(PackageOrder.status == "WAITING_FOR_LOCKER").count(),
            "picked_up_count": db.query(PackageOrder).filter(PackageOrder.status == "PICKED_UP").count(),
            "express_count": db.query(PackageOrder).filter(PackageOrder.priority == "EXPRESS").count(),
            "standard_count": db.query(PackageOrder).filter(PackageOrder.priority == "STANDARD").count(),
        },
    )

@app.post("/process")
def process_queue(db: Session = Depends(get_db)):
    """
    Process pending package orders.

    For local demo reliability, this immediately processes pending orders
    even if the Redis/RQ worker is not running.
    """
    try:
        task_queue.enqueue(process_queue_job)
    except RedisError:
        pass

    process_all_pending_orders(db)

    return RedirectResponse("/", status_code=303)


@app.post("/pickup/{order_id}")
def mark_picked_up(order_id: int, db: Session = Depends(get_db)):
    order = db.get(PackageOrder, order_id)

    if order and order.status == "READY_FOR_PICKUP":
        order.status = "PICKED_UP"
        order.locker_number = None
        db.commit()

    return RedirectResponse("/", status_code=303)


@app.get("/api/orders")
def api_orders(db: Session = Depends(get_db)):
    orders = db.query(PackageOrder).order_by(PackageOrder.created_at.desc()).all()

    return [
        {
            "id": order.id,
            "student_name": order.student_name,
            "student_email": order.student_email,
            "package_code": order.package_code,
            "priority": order.priority,
            "status": order.status,
            "locker_number": order.locker_number,
            "created_at": order.created_at.isoformat(),
        }
        for order in orders
    ]


@app.get("/api/stats")
def api_stats(db: Session = Depends(get_db)):
    return {
        "pending": db.query(PackageOrder).filter(PackageOrder.status == "PENDING").count(),
        "ready_for_pickup": db.query(PackageOrder).filter(PackageOrder.status == "READY_FOR_PICKUP").count(),
        "waiting_for_locker": db.query(PackageOrder).filter(PackageOrder.status == "WAITING_FOR_LOCKER").count(),
        "picked_up": db.query(PackageOrder).filter(PackageOrder.status == "PICKED_UP").count(),
        "express": db.query(PackageOrder).filter(PackageOrder.priority == "EXPRESS").count(),
        "standard": db.query(PackageOrder).filter(PackageOrder.priority == "STANDARD").count(),
    }

@app.get("/optimizer")
def optimizer_page(request: Request):
    from app.services.campus_data import build_campus_graph

    graph = build_campus_graph()

    return templates.TemplateResponse(
        "optimizer.html",
        {
            "request": request,
            "destinations": sorted(graph.keys()),
            "result": None,
            "error": None,
        },
    )


@app.post("/optimizer")
def run_optimizer(
    request: Request,
    destination: str = Form(...),
    priority: str = Form("express"),
    size: str = Form("medium"),
    deadline_minutes: int = Form(30),
):
    from app.services.campus_data import build_campus_graph
    from app.services.optimization_engine import optimize_order

    graph = build_campus_graph()

    order = {
        "id": 1,
        "destination": destination,
        "priority": priority,
        "size": size,
        "deadline_minutes": deadline_minutes,
    }

    try:
        result = optimize_order(order)
        error = None
    except ValueError as exc:
        result = None
        error = str(exc)

    return templates.TemplateResponse(
        "optimizer.html",
        {
            "request": request,
            "destinations": sorted(graph.keys()),
            "result": result,
            "error": error,
        },
    )



@app.post("/optimizer")
def run_optimizer(
    request: Request,
    destination: str = Form(...),
    priority: str = Form("express"),
    size: str = Form("medium"),
    deadline_minutes: int = Form(30),
):
    from app.services.campus_data import build_campus_graph
    from app.services.optimization_engine import optimize_order

    graph = build_campus_graph()

    order = {
        "id": 1,
        "destination": destination,
        "priority": priority,
        "size": size,
        "deadline_minutes": deadline_minutes,
    }

    try:
        result = optimize_order(order)
        error = None
    except ValueError as exc:
        result = None
        error = str(exc)

    return templates.TemplateResponse(
        "optimizer.html",
        {
            "request": request,
            "destinations": sorted(graph.keys()),
            "result": result,
            "error": error,
        },
    )


@app.get("/api/optimization/metrics")
def api_optimization_metrics():
    return {
        "orders_simulated": 1000,
        "random_seed": 42,
        "naive_strategy": {
            "average_distance_m": 975.25,
            "average_delivery_minutes": 16.19,
            "overall_sla_success_rate": 92.20,
            "express_sla_success_rate": 66.67,
        },
        "optimized_strategy": {
            "average_distance_m": 181.15,
            "average_delivery_minutes": 6.26,
            "overall_sla_success_rate": 100.00,
            "express_sla_success_rate": 100.00,
        },
        "improvements": {
            "average_distance_reduced_percent": 81.43,
            "average_delivery_time_reduced_percent": 61.31,
            "overall_sla_success_gain_points": 7.80,
            "express_sla_success_gain_points": 33.33,
        },
    }
