from __future__ import annotations
from datetime import UTC, datetime

from sqlalchemy import Column, Numeric, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base



class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    order_id = Column(String, primary_key=True, index=True, nullable=False)
    customer_id = Column(String, nullable=False, index=True)
    product_id = Column(String, nullable=False, index=True)

    quantity = Column(Integer, nullable=False)
    price_per_unit = Column(Numeric(10, 2), nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)

    status = Column(String, nullable=False)
    order_date = Column(DateTime, nullable=False)

    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
