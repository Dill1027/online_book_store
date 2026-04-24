import os
from typing import Optional

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import PyMongoError, ServerSelectionTimeoutError

from models import CartItem, CartItemCreate, CartItemUpdate


class DataStoreUnavailableError(Exception):
    """Raised when MongoDB is unavailable for cart operations."""


class CartMockDataService:
    def __init__(self):
        # Supports both mongodb:// and mongodb+srv:// formats.
        self.mongo_uri = os.getenv(
            "MONGODB_URI",
            "mongodb+srv://prabhathdilshan2001_db_user:12345@cart.an27bae.mongodb.net/cart_items",
        )
        # Optional fallback URI for DNS-sensitive environments.
        self.mongo_uri_fallback = os.getenv("MONGODB_URI_FALLBACK")

        self.db_name = self._extract_db_name(self.mongo_uri)
        self.collection_name = "cart_items"

        self.client: Optional[MongoClient] = None
        self.database: Optional[Database] = None
        self.collection: Optional[Collection] = None

    @staticmethod
    def _extract_db_name(uri: str) -> str:
        # URI examples:
        # mongodb://host:27017/dbname?retryWrites=true
        # mongodb+srv://host/dbname?retryWrites=true
        if "/" not in uri:
            return "smartlearn"

        db_segment = uri.rsplit("/", 1)[-1]
        db_name = db_segment.split("?", 1)[0].strip()
        return db_name or "smartlearn"

    def _connection_candidates(self) -> list[str]:
        candidates = [self.mongo_uri]
        if self.mongo_uri_fallback:
            candidates.append(self.mongo_uri_fallback)
        return candidates

    @staticmethod
    def _build_client(uri: str) -> MongoClient:
        return MongoClient(
            uri,
            serverSelectionTimeoutMS=10000,
            connectTimeoutMS=10000,
            socketTimeoutMS=10000,
            tls=True,
            retryWrites=True,
            connect=False,
        )

    def _ensure_connected(self) -> None:
        if self.collection is not None:
            return

        for uri in self._connection_candidates():
            try:
                client = self._build_client(uri)
                # Force server selection lazily and verify connectivity.
                client.admin.command("ping")

                self.client = client
                self.database = client[self.db_name]
                self.collection = self.database[self.collection_name]
                return
            except (ServerSelectionTimeoutError, PyMongoError):
                continue

        raise DataStoreUnavailableError("Cart datastore is unavailable")

    def ping(self) -> bool:
        """Health-check helper for external callers."""
        try:
            self._ensure_connected()
            self.client.admin.command("ping")
            return True
        except (ServerSelectionTimeoutError, PyMongoError, DataStoreUnavailableError):
            return False

    @staticmethod
    def _to_cart_item(document: dict | None) -> CartItem | None:
        if not document:
            return None

        normalized = {k: v for k, v in document.items() if k != "_id"}

        # Handle legacy field names and types from older cart records.
        if "book_title" not in normalized and "title" in normalized:
            normalized["book_title"] = normalized.get("title")

        if normalized.get("book_id") is not None:
            normalized["book_id"] = str(normalized["book_id"])

        for key in ("id", "customer_id", "quantity"):
            if normalized.get(key) is not None:
                normalized[key] = int(normalized[key])

        if normalized.get("price") is not None:
            normalized["price"] = float(normalized["price"])

        try:
            return CartItem(**normalized)
        except Exception:
            return None

    def _with_db_guard(self, operation):
        try:
            self._ensure_connected()
            return operation()
        except (ServerSelectionTimeoutError, PyMongoError, DataStoreUnavailableError) as exc:
            raise DataStoreUnavailableError("Cart datastore is unavailable") from exc

    def _next_id(self) -> int:
        latest = self.collection.find_one(sort=[("id", -1)])
        if not latest:
            return 1
        return int(latest.get("id", 0)) + 1

    def get_all_cart_items(self):
        def _op():
            docs = self.collection.find({})
            return [item for item in (self._to_cart_item(doc) for doc in docs) if item is not None]

        return self._with_db_guard(_op)

    def get_cart_item_by_id(self, item_id: int):
        return self._with_db_guard(
            lambda: self._to_cart_item(self.collection.find_one({"id": item_id}))
        )

    def get_cart_items_by_customer_id(self, customer_id: int):
        def _op():
            docs = self.collection.find({"customer_id": customer_id})
            return [self._to_cart_item(doc) for doc in docs]

        return self._with_db_guard(_op)

    def add_cart_item(self, item_data: CartItemCreate):
        def _op():
            new_item = CartItem(id=self._next_id(), **item_data.model_dump())
            self.collection.insert_one(new_item.model_dump())
            return new_item

        return self._with_db_guard(_op)

    def update_cart_item(self, item_id: int, item_data: CartItemUpdate):
        update_data = item_data.model_dump(exclude_unset=True)
        if not update_data:
            return self.get_cart_item_by_id(item_id)

        def _op():
            result = self.collection.update_one({"id": item_id}, {"$set": update_data})
            if result.matched_count == 0:
                return None
            return self.get_cart_item_by_id(item_id)

        return self._with_db_guard(_op)

    def delete_cart_item(self, item_id: int):
        return self._with_db_guard(
            lambda: self.collection.delete_one({"id": item_id}).deleted_count > 0
        )

    def clear_customer_cart(self, customer_id: int):
        return self._with_db_guard(
            lambda: self.collection.delete_many({"customer_id": customer_id}).deleted_count
        )
