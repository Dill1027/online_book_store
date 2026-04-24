import os
from datetime import date
from typing import Optional

from pymongo import MongoClient
from pymongo.errors import PyMongoError, ServerSelectionTimeoutError
from bson import ObjectId
from dotenv import load_dotenv

from config import MONGO_URI, DB_NAME, COLLECTION_NAME
from models import Order, OrderCreate, OrderUpdate

load_dotenv()

class OrderMockDataService:
    def __init__(self):
        mongo_uri = os.getenv("MONGODB_URI", MONGO_URI)
        mongo_uri_fallback = os.getenv("MONGODB_URI_FALLBACK")
        db_name = os.getenv("DB_NAME", DB_NAME)
        collection_name = os.getenv("COLLECTION_NAME", COLLECTION_NAME)

        self.client = None
        self.collection = None
        self.is_mock = False
        self.mock_orders = {}

        connection_candidates = [mongo_uri]
        if mongo_uri_fallback:
            connection_candidates.append(mongo_uri_fallback)

        for uri in connection_candidates:
            try:
                self.client = MongoClient(
                    uri,
                    serverSelectionTimeoutMS=3000,
                    connectTimeoutMS=3000,
                    socketTimeoutMS=3000,
                )
                self.client.admin.command("ping")
                self.collection = self.client[db_name][collection_name]
                break
            except (ServerSelectionTimeoutError, PyMongoError):
                self.client = None
                self.collection = None

        if self.collection is None:
            self.is_mock = True

    def _to_order(self, document):
        if not document:
            return None

        document = dict(document)
        document["id"] = str(document["_id"]) 
        document.pop("_id", None)

        return Order(**document)


    def get_all_orders(self):
        if self.is_mock:
            return list(self.mock_orders.values())

        docs = self.collection.find({})
        return [self._to_order(doc) for doc in docs]

    def get_order_by_id(self, order_id: str):
        if self.is_mock:
            return self.mock_orders.get(order_id)

        try:
            return self._to_order(self.collection.find_one({"_id": ObjectId(order_id)}))
        except Exception:
            return None

    def get_orders_by_customer_id(self, customer_id: str):
        if self.is_mock:
            return [order for order in self.mock_orders.values() if order.customer_id == customer_id]

        docs = self.collection.find({"customer_id": customer_id})
        return [self._to_order(doc) for doc in docs]

    def add_order(self, order_data: OrderCreate, total_amount: float, order_date: str, address: str):
        if self.is_mock:
            order_id = str(len(self.mock_orders) + 1)
            order = Order(
                id=order_id,
                customer_id=order_data.customer_id,
                items=order_data.items,
                total_amount=total_amount,
                status=order_data.status or "Pending",
                address=address,
                order_date=order_date or date.today().isoformat(),
            )
            self.mock_orders[order_id] = order
            return order

        order_dict = order_data.model_dump()

        order_dict["total_amount"] = total_amount
        order_dict["order_date"] = order_date
        order_dict["address"] = address

        result = self.collection.insert_one(order_dict)

        saved_order = self.collection.find_one({"_id": result.inserted_id})

        return self._to_order(saved_order)



    def update_order(self, order_id: str, order_data: OrderUpdate, total_amount: Optional[float] = None):
        if self.is_mock:
            existing = self.mock_orders.get(order_id)
            if not existing:
                return None

            update_data = order_data.model_dump(exclude_unset=True)
            if total_amount is not None:
                update_data["total_amount"] = total_amount

            if not update_data:
                return existing

            updated = existing.model_copy(update=update_data)
            self.mock_orders[order_id] = updated
            return updated

        update_data = order_data.model_dump(exclude_unset=True)

        if total_amount is not None:
            update_data["total_amount"] = total_amount

        if not update_data:
            return self.get_order_by_id(order_id)

        try:
            result = self.collection.update_one({"_id": ObjectId(order_id)}, {"$set": update_data})
        except Exception:
            return None

        if result.matched_count == 0:
            return None

        return self.get_order_by_id(order_id)

    def delete_order(self, order_id: str):
        if self.is_mock:
            return self.mock_orders.pop(order_id, None) is not None

        try:
            result = self.collection.delete_one({"_id": ObjectId(order_id)})
            return result.deleted_count > 0
        except Exception:
            return False