from pydantic import BaseModel, Field
from typing import Optional


class CartItem(BaseModel):
    id: int
    customer_id: int
    book_id: str
    book_title: Optional[str] = None
    quantity: int = Field(..., gt=0)
    price: Optional[float] = Field(default=None, ge=0)


class CartItemCreate(BaseModel):
    customer_id: int
    book_id: str
    book_title: Optional[str] = None
    quantity: int = Field(..., gt=0)
    price: Optional[float] = Field(default=None, ge=0)


class CartItemUpdate(BaseModel):
    customer_id: Optional[int] = None
    book_id: Optional[str] = None
    book_title: Optional[str] = None
    quantity: Optional[int] = Field(default=None, gt=0)
    price: Optional[float] = Field(default=None, ge=0)
