import uuid

from fastapi import Depends, FastAPI, Form
from fastapi.responses import RedirectResponse

from app.database import Base, engine, get_db
from app.models import PackageOrder
from app.queue_worker import process_all_pending_orders

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Campus Package Fulfillment System")


@app.get("/")
def dashboard():
    return {"message": "Campus Package Fulfillment System"}


@app.post("/orders")
def create_order(
    student_name=Form(...),
    student_email=Form(...),
    priority=Form("STANDARD"),
    db=Depends(get_db),
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
def process_queue(db=Depends(get_db)):
    process_all_pending_orders(db)
    return RedirectResponse("/", status_code=303)


@app.post("/pickup/{order_id}")
def mark_picked_up(order_id, db=Depends(get_db)):
    try:
        order_id = int(order_id)
    except ValueError:
        return RedirectResponse("/", status_code=303)

    order = db.get(PackageOrder, order_id)

    if order:
        order.status = "PICKED_UP"
        order.locker_number = None
        db.commit()

    return RedirectResponse("/", status_code=303)


@app.get("/api/orders")
def api_orders(db=Depends(get_db)):
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
def api_stats(db=Depends(get_db)):
    return {
        "pending": db.query(PackageOrder).filter(PackageOrder.status == "PENDING").count(),
        "ready_for_pickup": db.query(PackageOrder).filter(PackageOrder.status == "READY_FOR_PICKUP").count(),
        "waiting_for_locker": db.query(PackageOrder).filter(PackageOrder.status == "WAITING_FOR_LOCKER").count(),
        "picked_up": db.query(PackageOrder).filter(PackageOrder.status == "PICKED_UP").count(),
        "express": db.query(PackageOrder).filter(PackageOrder.priority == "EXPRESS").count(),
        "standard": db.query(PackageOrder).filter(PackageOrder.priority == "STANDARD").count(),
    }
