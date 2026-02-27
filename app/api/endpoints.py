from fastapi import APIRouter, Body, File, UploadFile, Depends, HTTPException
from typing import Optional, List
from pydantic import ValidationError
from sqlalchemy.orm import Session
import csv
import io
from datetime import datetime
from decimal import Decimal
from app.core.logging_config import logger
from app.core.metrics import ingestion_total, ingestion_errors_total

from app.database import get_db
from app.schemas.order import OrderIngest, OrderCreate
from app.models.orders import Order


router = APIRouter()

@router.post("/ingest")
async def ingest_data(
    file: Optional[UploadFile] = File(None),
    data: Optional[List[dict]] = Body(None),
    db: Session = Depends(get_db)
):
    """
    Accepting CSV or JSON files, and using SQLAlchemy to perform batch insert open a DB session, inject it into an\
    endpoint, and automatic close.
    """

    # ensuring either file or data is provided
    if not file and not data:
        raise HTTPException(status_code=400, detail="Must provide either CSV file or JSON data")
    if file and data:
        raise HTTPException(status_code=400, detail="Provide either CSV file or JSON data, not both")

    # parse data
    records = []
    if file:
        #csv data
        try:
            contents = await file.read()
            csv_text = contents.decode('utf8')
            csv_read = csv.DictReader(io.StringIO(csv_text))
            records = list(csv_reader)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error reading csv file: {str(e)}")
    else:
        # JSON data
        records = data



    # VALIDATION
    valid_records = []
    errors = []

    for idx, record in enumerate(records):
        try:
            order_ingest = OrderIngest(**record)

            total_amount = Decimal(order_ingest.quantity) * order_ingest.price_per_unit

            order_create = OrderCreate(**order_ingest.dict(), total_amount=total_amount)

            valid_records.append(order_create)

        except ValidationError as e:
            errors.apend({"row": idx + 1, "data":record, "error":str(e)})

        except ExceptionError as e: 
            errors.apend({"row": idx + 1, "data":record, "error":f"unexpected error: {str(e)}"})



    # BATCH INSERT
    inserted_count = 0

    if valid_records:
        try:
            # Convert to database models
            db_orders = [
                Order(
                    order_id=order.order_id,
                    customer_id=order.customer_id,
                    product_id=order.product_id,
                    quantity=order.quantity,
                    price_per_unit=order.price_per_unit,
                    order_date=order.order_date,
                    status=order.status,
                    total_amount=order.total_amount,
                    created_at=datetime.utcnow()
                )
                for order in valid_records
            ]

            # Batch insert
            db.bulk_save_objects(db_orders)
            db.commit()
            inserted_count = len(db_orders)
            ingestion_total.inc(inserted_count)

        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Database error: {str(e)}"
                ingestion_errors_total.inc(len(errors))
            )

    # RETURN
    return {
        "status": "completed",
        "total_submitted": len(records),
        "successful": inserted_count,
        "failed": len(errors),
        "errors": errors[:10] if errors else []
    }





@router.get("/orders")
async def get_all_orders(skip: int = 0,
                        limit: int = 10,
                        customer_id: Optional[str] = None,
                        status: Optional[str] = None,
                        db: Session=Depends(get_db)):
    logger.info(f"Fetching orders - skip={skip}, limit={limit}, customer_id={customer_id}, status={status}")

    query = db.query(Order)

    if customer_id:
        query = query.filter(Order.customer_id == customer_id)
        logger.debug(f"Filtering by customer_id: {customer_id}")

    if status:
        query = query.filter(Order.status == status)
        logger.debug(f"Filtering by status: {status}")

    orders = db.query(Order).offset(skip).limit(limit).all()
    logger.info(f"Retrieved {len(orders)} orders")

    return orders



@router.get("/orders/{order_id}")
def get_order(order_id: str, db: Session = Depends(get_db)):
    logger.info(f"Fetching order with ID: {order_id}")

    order = db.query(Order).filter(Order.order_id == order_id).first()

    if order is None:
        logger.warning(f"Order not found: {order_id}")
        raise HTTPException(status_code=404, detail="Order not found")

    logger.info(f"Order found: {order_id}")
    return order
