from pydantic import BaseModel, Field
from typing import List, Optional


class Item(BaseModel):
    book_id: int
    title: str
    quantity: int 
    price: float 


class Order(BaseModel):
    id: int
    customer_id: int
    items: List[Item]
    total_amount: float
    status: str
    address: str
    order_date: str

class OrderCreate(BaseModel):
    customer_id: int
    items: List[Item]
    status: Optional[str] = "PLACED"
    address: str

class OrderUpdate(BaseModel):
    customer_id: Optional[int] = None
    items: Optional[List[Item]] = None
    status: Optional[str] = None
    address: Optional[str] = None
