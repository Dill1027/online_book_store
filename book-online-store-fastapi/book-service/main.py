from fastapi import FastAPI, HTTPException, status

from data_service import BookDataService
from models import Book, BookCreate
from service import BookService

app = FastAPI(title="book-service")

book_service = BookService(BookDataService())


@app.get("/health")
def health() -> dict[str, str]:
    return {"service": "book-service", "status": "ok"}


@app.get("/books")
def list_books() -> list[Book]:
    return book_service.list_books()


@app.get("/books/{book_id}")
def get_book_by_book_id(book_id: str) -> Book:
    book = book_service.get_book_by_book_id(book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return book


@app.post("/books", status_code=status.HTTP_201_CREATED)
def create_book(payload: BookCreate) -> Book:
    try:
        return book_service.create_book(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
