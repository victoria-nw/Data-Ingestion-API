from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from decimal import Decimal


class OrderIngest(BaseModel):
    order_id: str = Field(..., min_length=1, pattern=r'^ORD-\d{5,}$', description="unique order identifier")
    customer_id: str = Field(..., min_length=1, pattern=r'^CUST-\d{5,}$', description="unique customer identifier")
    product_id: str = Field(..., min_length=1, pattern=r'^PROD-\d{5,}$', description="unique product identifier")
    quantity: int = Field(..., gt=0, description="Quantity ordered")
    price_per_unit: Decimal = Field(..., gt=0, description="Price per unit")
    order_date: datetime
    status: Optional[str] = Field(default="pending", pattern=r'^(pending|shipped|completed|cancelled)$', description="Ordder status")


class OrderCreate(OrderIngest):
    total_amount: Decimal = Field(..., gt=0, description="Total amount")


class OrderResponse(OrderCreate):
    created_at: datetime

    class Config:
        orm_mode = True
