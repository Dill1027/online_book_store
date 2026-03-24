import os

from pymongo import MongoClient

from models import CartItem, CartItemCreate, CartItemUpdate


class CartMockDataService:
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
        self.collection = self.client["smartlearn"]["cart_items"]

    @staticmethod
    def _to_cart_item(document: dict | None) -> CartItem | None:
        if not document:
            return None
        document.pop("_id", None)
        return CartItem(**document)

    def _next_id(self) -> int:
        latest = self.collection.find_one(sort=[("id", -1)])
        if not latest:
            return 1
        return int(latest.get("id", 0)) + 1

    def get_all_cart_items(self):
        docs = self.collection.find({})
        return [self._to_cart_item(doc) for doc in docs]

    def get_cart_item_by_id(self, item_id: int):
        return self._to_cart_item(self.collection.find_one({"id": item_id}))

    def get_cart_items_by_customer_id(self, customer_id: int):
        docs = self.collection.find({"customer_id": customer_id})
        return [self._to_cart_item(doc) for doc in docs]

    def add_cart_item(self, item_data: CartItemCreate):
        new_item = CartItem(id=self._next_id(), **item_data.model_dump())
        self.collection.insert_one(new_item.model_dump())
        return new_item

    def update_cart_item(self, item_id: int, item_data: CartItemUpdate):
        update_data = item_data.model_dump(exclude_unset=True)
        if not update_data:
            return self.get_cart_item_by_id(item_id)

        result = self.collection.update_one({"id": item_id}, {"$set": update_data})
        if result.matched_count == 0:
            return None
        return self.get_cart_item_by_id(item_id)

    def delete_cart_item(self, item_id: int):
        result = self.collection.delete_one({"id": item_id})
        return result.deleted_count > 0

    def clear_customer_cart(self, customer_id: int):
        result = self.collection.delete_many({"customer_id": customer_id})
        return result.deleted_count
