from pydantic import BaseModel, Field
from typing import Optional


class Customer(BaseModel):
    id: str
    name: str = Field(..., min_length=2, max_length=100)
    email: str
    phone: str = Field(..., min_length=9, max_length=15)
    address: str = Field(..., min_length=3, max_length=255)


class CustomerCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: str
    phone: str = Field(..., min_length=9, max_length=15)
    address: str = Field(..., min_length=3, max_length=255)


class CustomerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[str] = None
    phone: Optional[str] = Field(None, min_length=9, max_length=15)
    address: Optional[str] = Field(None, min_length=3, max_length=255)