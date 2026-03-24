from pydantic import BaseModel
from typing import Optional


class Customer(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    address: str


class CustomerCreate(BaseModel):
    name: str
    email: str
    phone: str
    address: str


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None