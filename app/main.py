from fastapi import FastAPI, Depends, Response
from app.db import get_connection
from app.schemas.event import event
from app.database.init_db import init_db
from decimal import Decimal
from sqlalchemy.orm import Session
from datetime import datetime, UTC
from app.core.logging_config import logger
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
from app.core.exception_handlers import (validation_exception_handler, integrity_error_handler, general_exception_handler)
from sqlalchemy import text
from app.core.metrics import generate_latest, CONTENT_TYPE_LATEST, orders_created_total

from app.database import get_db
from app.schemas.order import OrderIngest, OrderResponse
from app.models import Order
from app.api.endpoints import router as ingest_router

app = FastAPI(title="Data Ingestion Service")

app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(IntegrityError, integrity_error_handler)
app.add_exception_handler(Exception, general_exception_handler)

app.include_router(ingest_router, tags=["ingestion"])

@app.get("/health")
def health():
    logger.info("Health check requested")
    return {"status": "ok"}



@app.get("/db/health")
def db_health(db: Session = Depends(get_db)):
    logger.info("Database health check requested")
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
                cur.fetchone()
        return {"database": "healthy"}
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return {
            "database": "unhealthy",
            "detail": str(e),
            "timestamp": datetime.now(UTC).isoformat()
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

    logger.info(f"Creating order: {order.order_id}")
    total_amount = Decimal(order.quantity) * order.price_per_unit

    try:
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

        orders_created_total.inc()

        logger.info("Order successfully created: {order.order_id}")
        return db_order

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create order {order.order_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.get("/metrics")
def metrics():
    logger.info("Metrics requested")
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.on_event("startup")
async def startup_event():
    logger.info("Application starting up")
    logger.info("Database connection established")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutting down")

init_db()
