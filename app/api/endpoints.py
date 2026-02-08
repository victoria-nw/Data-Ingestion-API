from fastapi import APIRouter, Body, File, UploadFile, Depends, HTTPException
from typing import Optional, List
from pydantic import ValidationError
from sqlalchemy.orm import Session
import csv
import io
from datetime import datetime
from decimal import Decimal

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

        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Database error: {str(e)}"
            )

    # RETURN
    return {
        "status": "completed",
        "total_submitted": len(records),
        "successful": inserted_count,
        "failed": len(errors),
        "errors": errors[:10] if errors else []
    }
