from fastapi import FastAPI, Depends
from app.db import get_connection
from app.schemas.event import event
from app.database.init_db import init_db
from decimal import Decimal
from sqlalchemy.orm import Session
from datetime import datetime, UTC

from app.database import get_db
from app.schemas.order import OrderIngest, OrderResponse
from app.models import Order
from app.api.endpoints import router as ingest_router

app = FastAPI(title="Data Ingestion Service")

app.include_router(ingest_router, tags=["ingestion"])

@app.get("/health")
def health():
    return {"status": "ok"}



@app.get("/db/health")
def db_health():
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
                cur.fetchone()
        return {"database": "ok"}
    except Exception as e:
        return {
            "database": "error",
            "detail": str(e)
        }



@app.post("/events")
def ingest_event(event: event):
    return {
        "message": "event received",
        "event": event
        }


@app.post("/orders", response_model=OrderResponse)
def create_order(order: OrderIngest, db: Session = Depends(get_db)):
    """
    Create a new order
    """
    
    total_amount = Decimal(order.quantity) * order.price_per_unit
    
    db_order = Order(
        order_id=order.order_id,
        customer_id=order.customer_id,
        product_id=order.product_id,
        quantity=order.quantity,
        price_per_unit=order.price_per_unit,
        order_date=order.order_date,
        status=order.status,
        total_amount=total_amount,
        created_at=datetime.now(UTC)
    )
    
    db.add(db_order)
    db.commit()
    db.refresh(db_order)  
    
    return db_order



@app.on_event("startup")
def startup_event():
    init_db()



