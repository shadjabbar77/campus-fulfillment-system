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
    orders = db.query(PackageOrder).order_by(PackageOrder.created_at.desc()).all()

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "orders": orders,
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
    db: Session = Depends(get_db),
):
    priority = priority.upper()

    if priority not in ["STANDARD", "EXPRESS"]:
        priority = "STANDARD"

    package_code = f"PKG-{uuid.uuid4().hex[:8].upper()}"

    order = PackageOrder(
        student_name=student_name,
        student_email=student_email,
        package_code=package_code,
        priority=priority,
        status="PENDING",
    )

    db.add(order)
    db.commit()

    return RedirectResponse("/", status_code=303)


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

    if order:
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
