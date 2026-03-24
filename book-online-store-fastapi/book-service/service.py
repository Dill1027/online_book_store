from models import Book, BookCreate
from data_service import BookDataService


class BookService:
    def __init__(self, data_service: BookDataService) -> None:
        self.data_service = data_service

    def list_books(self) -> list[Book]:
        return self.data_service.list_books()

    def get_book_by_book_id(self, book_id: str) -> Book | None:
        return self.data_service.get_book_by_id(book_id)

    def create_book(self, payload: BookCreate) -> Book:
        return self.data_service.create_book(payload)
