# book-service/main.py

from fastapi import FastAPI, HTTPException, status, Query
from models import Book, BookCreate, BookUpdate
from service import BookService
from typing import List, Optional

app = FastAPI(title="Book Microservice", version="1.0.0")

# Initialize service
book_service = BookService()


@app.get("/")
def read_root():
    return {"message": "Book Microservice is running"}


# ✅ Get all books + search
@app.get("/api/books", response_model=List[Book])
def get_all_books(
    title: Optional[str] = Query(None),
    author: Optional[str] = Query(None),
    category: Optional[str] = Query(None)
):
    """Get all books (with optional search by title, author, category)"""
    return book_service.get_all(title, author, category)


# ✅ Get book by ID
@app.get("/api/books/{book_id}", response_model=Book)
def get_book(book_id: int):
    """Get a book by ID"""
    book = book_service.get_by_id(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


# ✅ Create book
@app.post("/api/books", response_model=Book, status_code=status.HTTP_201_CREATED)
def create_book(book: BookCreate):
    """Create a new book"""
    return book_service.create(book)


# ✅ Update book
@app.put("/api/books/{book_id}", response_model=Book)
def update_book(book_id: int, book: BookUpdate):
    """Update a book"""
    updated_book = book_service.update(book_id, book)
    if not updated_book:
        raise HTTPException(status_code=404, detail="Book not found")
    return updated_book


# ✅ Delete book
@app.delete("/api/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int):
    """Delete a book"""
    success = book_service.delete(book_id)
    if not success:
        raise HTTPException(status_code=404, detail="Book not found")
    return None