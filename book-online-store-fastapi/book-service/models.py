from pydantic import BaseModel, Field
from typing import Optional


class Book(BaseModel):
    id: int
    title: str
    author: str
    price: float = Field(..., ge=0)
    category: str
    stock: int = Field(..., ge=0)


class BookCreate(BaseModel):
    title: str
    author: str
    price: float = Field(..., ge=0)
    category: str
    stock: int = Field(..., ge=0)


class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    price: Optional[float] = Field(default=None, ge=0)
    category: Optional[str] = None
    stock: Optional[int] = Field(default=None, ge=0)
