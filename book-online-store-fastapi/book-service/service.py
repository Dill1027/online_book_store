# book-service/service.py

from data_service import BookDataService

class BookService:

    def __init__(self):
        self.data_service = BookDataService()

    # Get all books (with optional search)
    def get_all(self, title: str = None, author: str = None, category: str = None):
        return self.data_service.get_all_books(title, author, category)

    # Get book by ID
    def get_by_id(self, book_id: int):
        return self.data_service.get_book_by_id(book_id)

    # Create new book
    def create(self, book_data):
        return self.data_service.add_book(book_data)

    # Update book
    def update(self, book_id: int, book_data):
        return self.data_service.update_book(book_id, book_data)

    # Delete book
    def delete(self, book_id: int):
        return self.data_service.delete_book(book_id)