# book-service/models.py

from pydantic import BaseModel
from typing import Optional

# Main Book Model (response model)
class Book(BaseModel):
    id: int
    title: str
    author: str
    category: str
    price: float
    stock: int


# Model for creating a new book
class BookCreate(BaseModel):
    title: str
    author: str
    category: str
    price: float
    stock: int


# Model for updating a book (all optional fields)
class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None