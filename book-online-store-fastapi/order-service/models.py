from pydantic import BaseModel, Field
from typing import List, Optional


class Item(BaseModel):
    book_id: str
    title: str
    quantity: int 
    price: float 


class Order(BaseModel):
    id: str
    customer_id: str
    items: List[Item]
    total_amount: float
    status: str
    address: str
    order_date: str

class OrderCreate(BaseModel):
    customer_id: str
    items: List[Item]
    status: Optional[str] = "Pending"
    address: str

class OrderUpdate(BaseModel):
    customer_id: Optional[str] = None
    items: Optional[List[Item]] = None
    status: Optional[str] = None
    address: Optional[str] = None
