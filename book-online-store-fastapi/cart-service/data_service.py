import os
from typing import Optional

from pymongo import MongoClient
from pymongo.errors import PyMongoError

from models import CartItem, CartItemCreate, CartItemUpdate


class DataStoreUnavailableError(Exception):
    """Raised when MongoDB is unavailable for cart operations."""


class CartMockDataService:
    def __init__(self):
        mongo_uri = os.getenv(
            "MONGODB_URI",
            "mongodb+srv://smartlearn:1234@cluster0.9ypskee.mongodb.net/smartlearn",
        )

        self._init_error: Optional[str] = None
        self.client: Optional[MongoClient] = None
        self.collection = None

        try:
            # Lazy connect avoids startup crash if DNS/TLS to Atlas is unstable.
            self.client = MongoClient(
                mongo_uri,
                serverSelectionTimeoutMS=3000,
                connectTimeoutMS=3000,
                socketTimeoutMS=3000,
                connect=False,
            )
            self.collection = self.client["smartlearn"]["cart_items"]
        except PyMongoError as exc:
            self._init_error = str(exc)

    @staticmethod
    def _to_cart_item(document: dict | None) -> CartItem | None:
        if not document:
            return None
        document.pop("_id", None)
        return CartItem(**document)

    def _ensure_collection(self) -> None:
        if self.collection is None:
            reason = self._init_error or "MongoDB client is not initialized"
            raise DataStoreUnavailableError(reason)

    @staticmethod
    def _wrap_db_error(exc: Exception) -> DataStoreUnavailableError:
        return DataStoreUnavailableError(str(exc))

    def _next_id(self) -> int:
        self._ensure_collection()
        try:
            latest = self.collection.find_one(sort=[("id", -1)])
            if not latest:
                return 1
            return int(latest.get("id", 0)) + 1
        except PyMongoError as exc:
            raise self._wrap_db_error(exc) from exc

    def get_all_cart_items(self):
        self._ensure_collection()
        try:
            docs = self.collection.find({})
            return [self._to_cart_item(doc) for doc in docs]
        except PyMongoError as exc:
            raise self._wrap_db_error(exc) from exc

    def get_cart_item_by_id(self, item_id: int):
        self._ensure_collection()
        try:
            return self._to_cart_item(self.collection.find_one({"id": item_id}))
        except PyMongoError as exc:
            raise self._wrap_db_error(exc) from exc

    def get_cart_items_by_customer_id(self, customer_id: int):
        self._ensure_collection()
        try:
            docs = self.collection.find({"customer_id": customer_id})
            return [self._to_cart_item(doc) for doc in docs]
        except PyMongoError as exc:
            raise self._wrap_db_error(exc) from exc

    def add_cart_item(self, item_data: CartItemCreate):
        self._ensure_collection()
        try:
            new_item = CartItem(id=self._next_id(), **item_data.model_dump())
            self.collection.insert_one(new_item.model_dump())
            return new_item
        except PyMongoError as exc:
            raise self._wrap_db_error(exc) from exc

    def update_cart_item(self, item_id: int, item_data: CartItemUpdate):
        self._ensure_collection()
        update_data = item_data.model_dump(exclude_unset=True)
        if not update_data:
            return self.get_cart_item_by_id(item_id)

        try:
            result = self.collection.update_one({"id": item_id}, {"$set": update_data})
            if result.matched_count == 0:
                return None
            return self.get_cart_item_by_id(item_id)
        except PyMongoError as exc:
            raise self._wrap_db_error(exc) from exc

    def delete_cart_item(self, item_id: int):
        self._ensure_collection()
        try:
            result = self.collection.delete_one({"id": item_id})
            return result.deleted_count > 0
        except PyMongoError as exc:
            raise self._wrap_db_error(exc) from exc

    def clear_customer_cart(self, customer_id: int):
        self._ensure_collection()
        try:
            result = self.collection.delete_many({"customer_id": customer_id})
            return result.deleted_count
        except PyMongoError as exc:
            raise self._wrap_db_error(exc) from exc
