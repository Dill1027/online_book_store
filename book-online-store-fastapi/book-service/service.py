from typing import Optional
from data_service import BookMockDataService


class BookService:
    def __init__(self):
        self.data_service = BookMockDataService()

    def get_all(self, category: Optional[str] = None):
        return self.data_service.get_all_books(category)

    def get_by_id(self, book_id: int):
        return self.data_service.get_book_by_id(book_id)

    def create(self, book_data):
        return self.data_service.add_book(book_data)

    def update(self, book_id: int, book_data):
        return self.data_service.update_book(book_id, book_data)

    def delete(self, book_id: int):
        return self.data_service.delete_book(book_id)
