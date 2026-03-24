from models import Book, BookCreate, utcnow


class BookDataService:
    def __init__(self) -> None:
        self._books: dict[str, Book] = {}

    def list_books(self) -> list[Book]:
        return list(self._books.values())

    def get_book_by_id(self, book_id: str) -> Book | None:
        return self._books.get(book_id)

    def create_book(self, payload: BookCreate) -> Book:
        if payload.bookId in self._books:
            raise ValueError("Book with this bookId already exists")

        created = Book(**payload.model_dump())
        created.updatedAt = utcnow()
        self._books[created.bookId] = created
        return created
