import os
from typing import Optional

from pymongo import MongoClient

from models import Book, BookCreate, BookUpdate


class BookMockDataService:
    def __init__(self):
        mongo_uri = os.getenv(
            "MONGODB_URI",
            "mongodb+srv://smartlearn:1234@cluster0.9ypskee.mongodb.net/smartlearn"
        )
        self.client = MongoClient(
            mongo_uri,
            serverSelectionTimeoutMS=3000,
            connectTimeoutMS=3000,
            socketTimeoutMS=3000
        )
        self.collection = self.client["smartlearn"]["books"]

    @staticmethod
    def _to_book(document: dict | None) -> Book | None:
        if not document:
            return None
        document.pop("_id", None)
        return Book(**document)

    def _next_id(self) -> int:
        latest = self.collection.find_one(sort=[("id", -1)])
        if not latest:
            return 1
        return int(latest.get("id", 0)) + 1

    def get_all_books(self, category: Optional[str] = None):
        query = {"category": category} if category else {}
        docs = self.collection.find(query)
        return [self._to_book(doc) for doc in docs]

    def get_book_by_id(self, book_id: int):
        return self._to_book(self.collection.find_one({"id": book_id}))

    def add_book(self, book_data: BookCreate):
        new_book = Book(id=self._next_id(), **book_data.model_dump())
        self.collection.insert_one(new_book.model_dump())
        return new_book

    def update_book(self, book_id: int, book_data: BookUpdate):
        update_data = book_data.model_dump(exclude_unset=True)
        if not update_data:
            return self.get_book_by_id(book_id)

        result = self.collection.update_one({"id": book_id}, {"$set": update_data})
        if result.matched_count == 0:
            return None
        return self.get_book_by_id(book_id)

    def delete_book(self, book_id: int):
        result = self.collection.delete_one({"id": book_id})
        return result.deleted_count > 0
