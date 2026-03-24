from typing import List, Optional
from models import Book, BookCreate, BookUpdate


class BookMockDataService:
    def __init__(self):
        self.books: List[Book] = [
            Book(id=1, title="Clean Code", author="Robert C. Martin", price=4500, category="Programming", stock=10),
            Book(id=2, title="Atomic Habits", author="James Clear", price=3500, category="Self Help", stock=15),
            Book(id=3, title="The Pragmatic Programmer", author="Andrew Hunt", price=5000, category="Programming", stock=8),
        ]
        self.next_id = 4

    def get_all_books(self, category: Optional[str] = None):
        if category:
            return [book for book in self.books if book.category.lower() == category.lower()]
        return self.books

    def get_book_by_id(self, book_id: int):
        return next((book for book in self.books if book.id == book_id), None)

    def add_book(self, book_data: BookCreate):
        new_book = Book(id=self.next_id, **book_data.model_dump())
        self.books.append(new_book)
        self.next_id += 1
        return new_book

    def update_book(self, book_id: int, book_data: BookUpdate):
        book = self.get_book_by_id(book_id)
        if book:
            update_data = book_data.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(book, key, value)
            return book
        return None

    def delete_book(self, book_id: int):
        book = self.get_book_by_id(book_id)
        if book:
            self.books.remove(book)
            return True
        return False
