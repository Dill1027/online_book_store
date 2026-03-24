from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


OrderStatus = Literal["Pending", "Confirmed", "Shipped", "Delivered", "Cancelled"]


class OrderBase(BaseModel):
    orderId: str = Field(pattern=r"^O\d{3}$")
    customerId: str = Field(pattern=r"^C\d{3}$")
    bookId: str = Field(pattern=r"^B\d{3}$")
    title: str = Field(min_length=1)
    price: float = Field(ge=0)
    quantity: int = Field(ge=1)
    status: OrderStatus = "Pending"


class OrderCreate(OrderBase):
    pass


class Order(OrderBase):
    createdAt: datetime = Field(default_factory=utcnow)
    updatedAt: datetime = Field(default_factory=utcnow)
