from pydantic import BaseModel, Field
from typing import List, Optional


class OrderItem(BaseModel):
    book_id: int
    title: str
    quantity: int = Field(..., gt=0)
    price: float = Field(..., ge=0)


class Order(BaseModel):
    id: int
    customer_id: int
    items: List[OrderItem]
    total_amount: float
    status: str
    order_date: str


class OrderCreate(BaseModel):
    customer_id: int
    items: List[OrderItem]
    status: Optional[str] = "PLACED"


class OrderUpdate(BaseModel):
    customer_id: Optional[int] = None
    items: Optional[List[OrderItem]] = None
    status: Optional[str] = None
