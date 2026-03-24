from typing import List, Optional
from fastapi import FastAPI, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from models import Book, BookCreate, BookUpdate
from service import BookService

app = FastAPI(title="Book Service", version="1.0.0")
book_service = BookService()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Book Service is running"}


@app.get("/api/books", response_model=List[Book])
def get_all_books(category: Optional[str] = Query(default=None)):
    return book_service.get_all(category)


@app.get("/api/books/{book_id}", response_model=Book)
def get_book(book_id: int):
    book = book_service.get_by_id(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@app.post("/api/books", response_model=Book, status_code=status.HTTP_201_CREATED)
def create_book(book: BookCreate):
    return book_service.create(book)


@app.put("/api/books/{book_id}", response_model=Book)
def update_book(book_id: int, book: BookUpdate):
    updated_book = book_service.update(book_id, book)
    if not updated_book:
        raise HTTPException(status_code=404, detail="Book not found")
    return updated_book


@app.delete("/api/books/{book_id}")
def delete_book(book_id: int):
    success = book_service.delete(book_id)
    if not success:
        raise HTTPException(status_code=404, detail="Book not found")
    return {"message": "Book deleted successfully"}
