from app.database import SessionLocal
from app.queue_worker import process_all_pending_orders


def process_queue_job():
    db = SessionLocal()

    try:
        processed_orders = process_all_pending_orders(db)
        return [order.id for order in processed_orders]
    finally:
        db.close()