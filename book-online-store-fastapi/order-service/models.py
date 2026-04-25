from pydantic import BaseModel, Field, field_validator
from typing import List, Optional


class Item(BaseModel):
    book_id: str = Field(..., description="Book identifier")
    title: str = Field(..., description="Book title")
    quantity: int = Field(..., description="Quantity ordered")
    price: float = Field(..., description="Unit price")

    @field_validator("quantity")
    @classmethod
    def validate_quantity(cls, value: int) -> int:
        if value < 1:
            raise ValueError("Quantity must be at least 1")
        return value

    @field_validator("price")
    @classmethod
    def validate_price(cls, value: float) -> float:
        if value < 0:
            raise ValueError("Price must be greater than or equal to 0")
        return value


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
    customer_id: str
    items: List[Item]
    status: str
    address: str
