import os
from typing import Optional
from pymongo import MongoClient
from dotenv import load_dotenv
from models import Order, OrderCreate, OrderUpdate

load_dotenv()

class OrderMockDataService:
    def __init__(self):
        mongo_uri = os.getenv("MONGODB_URI")
        db_name = os.getenv("DB_NAME")
        collection_name = os.getenv("COLLECTION_NAME")

        self.client = MongoClient(
            mongo_uri,
            serverSelectionTimeoutMS=3000,
            connectTimeoutMS=3000,
            socketTimeoutMS=3000
        )

        self.collection = self.client[db_name][collection_name]

    @staticmethod
    def _to_order(document: dict | None) -> Order | None:
        if not document:
            return None
        document.pop("_id", None)
        return Order(**document)

    def _next_id(self) -> int:
        latest = self.collection.find_one(sort=[("id", -1)])
        if not latest:
            return 1
        return int(latest.get("id", 0)) + 1

    def get_all_orders(self):
        docs = self.collection.find({})
        return [self._to_order(doc) for doc in docs]

    def get_order_by_id(self, order_id: int):
        return self._to_order(self.collection.find_one({"id": order_id}))

    def add_order(self, order_data: OrderCreate, total_amount: float, order_date: str, address: str):
        new_order = Order(
            id=self._next_id(),
            customer_id=order_data.customer_id,
            items=order_data.items,
            total_amount=total_amount,
            status=order_data.status or "PLACED",
            address=address,
            order_date=order_date,
        )
        self.collection.insert_one(new_order.model_dump())
        return new_order

    def update_order(self, order_id: int, order_data: OrderUpdate, total_amount: Optional[float] = None):
        update_data = order_data.model_dump(exclude_unset=True)

        if total_amount is not None:
            update_data["total_amount"] = total_amount

        if not update_data:
            return self.get_order_by_id(order_id)

        result = self.collection.update_one({"id": order_id}, {"$set": update_data})

        if result.matched_count == 0:
            return None

        return self.get_order_by_id(order_id)

    def delete_order(self, order_id: int):
        result = self.collection.delete_one({"id": order_id})
        return result.deleted_count > 0