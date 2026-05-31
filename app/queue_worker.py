from sqlalchemy import case
        (PackageOrder.priority == "EXPRESS", 0),
from sqlalchemy.orm import Session

from app.models import PackageOrder

LOCKERS = ["A1", "A2", "A3", "B1", "B2", "B3", "C1", "C2", "C3"]


def get_available_locker(db: Session):
    active_orders = (
        db.query(PackageOrder)
        .filter(PackageOrder.status == "READY_FOR_PICKUP")
        .all()
    )

    used_lockers = {order.locker_number for order in active_orders}

    for locker in LOCKERS:
        if locker not in used_lockers:
            return locker

    return None


def process_next_order(db: Session):
    priority_order = case(
        else_=1,
    )

    order = (
        db.query(PackageOrder)
        .filter(PackageOrder.status == "PENDING")
        .order_by(priority_order, PackageOrder.created_at)
        .first()
    )

    if not order:
        return None

    locker = get_available_locker(db)

    if locker is None:
        order.status = "WAITING_FOR_LOCKER"
    else:
        order.status = "READY_FOR_PICKUP"
from fastapi.templating import Jinja2Templates
        order.locker_number = locker

    db.commit()
    db.refresh(order)

    return order


def process_all_pending_orders(db: Session):
    processed_orders = []

    while True:
        order = process_next_order(db)

        if order is None:
            break

        processed_orders.append(order)

        if order.status == "WAITING_FOR_LOCKER":
            break

    return processed_orders
